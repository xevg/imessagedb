from datetime import datetime
import re
import imessagedb
from imessagedb.message import Message
from imessagedb.messages import Messages
from alive_progress import alive_bar


def _generate_thread_row(message: Message) -> str:
    if message.is_from_me:
        style = 'me'
    else:
        style = 'them'

    text = message.text
    row_string = f'{" ":16s}<tr>\n' \
                 f'{" ":18s}<td class="reply_text_thread">\n' \
                 f'{" ":20s}<a href="#{message.rowid}">\n' \
                 f'{" ":22s}<button class="reply_text_{style}"> {text}</button>\n' \
                 f'{" ":20s}</a>\n' \
                 f'{" ":18s}</td>\n' \
                 f'{" ":16s}</tr>\n'
    return row_string


def _generate_thread_table(message_list: list, style: str) -> str:
    table_string = f'{" ":14s}<table class="thread_table_{style}">\n'
    for message in message_list:
        table_string = f'{table_string}{_generate_thread_row(message)}'
    table_string = f'{table_string}' \
                   f'{" ":14s}</table>\n' \
                   f'{" ":14s}<p>\n'
    return table_string


url_pattern = re.compile(r"((https?):((//)|(\\\\))+[\w\d:#@%/;$()~_?\+-=\\\.&]*)", re.MULTILINE | re.UNICODE)
mailto_pattern = re.compile(r"([\w\-\.]+@(\w[\w\-]+\.)+[\w\-]+)", re.MULTILINE | re.UNICODE)


def _replace_url_to_link(value: str) -> str:
    """ From https://gist.github.com/guillaumepiot/4539986 """

    # Replace url to link
    value = url_pattern.sub(r'<a href="\1" target="_blank">\1</a>', value)
    # Replace email to mailto
    value = mailto_pattern.sub(r'<a href="mailto:\1">\1</a>', value)
    return value


class HTMLOutput:
    """ Creates an HTML file (or string) from a Messages list

    ...

    There are a number of options in the configuration file that affect how the HTML is created.
    In the CONTROL section, the following impact the output:

    copy = True :
                If the attachments are not copied, they are not available on the HTML output.
                There are two reasons for that. 1) The web browser does not have access to the directory
                that the attachments are stored, so it cannot display them 2) Some of the attachments need
                to be converted in order to be viewed in the browser, and need a place to live.

    skip attachments = False :
                If true, attachments will not be available in the HTML output

    In the DISPLAY section, the following impact the output:

    inline attachments = False :
                If inline attachments are true, then the images will be part of the HTML. If
                it is false, then there will be a popup when you hover over the attachment text that will show
                the attachment on demand. This will make the load much faster and the output far less cluttered.

    me = Me :
                The name to put for your part of the conversation. It defaults to 'Me'.

    me html background color = AliceBlue
    them html background color = Lavender :
                The background color of the text messages for you and for the other person.
                The options for colors can be found here: https://www.w3schools.com/cssref/css_colors.php


    thread background = HoneyDew
    me thread background = AliceBlue
    them thread background = Lavender :
                The background color of the thread in replies

    me html name color = Blue
    them html name color = Purple :
                The color of the name

    """

    def __init__(self, database, me: str, person: str, message_list: Messages,
                 inline=False, output_file=None) -> None:
        """
            Parameters
            ----------
            database : imessagedb.DB
                An instance of a connected database

            me : str
                Your display name

            person : str
                The name of the person in the conversation

            message_list: imessagedb.DB.Messages
                 The messages

            inline : bool
                Display attachments inline or not

            output_filename : str
                The name of the output file"""

        self._database = database
        self._me = me
        self._person = person
        self._message_list = message_list
        self._attachment_list = self._database.attachment_list
        self._inline = inline
        self._output_file = output_file

        self._day = 'UNK'
        self._html_array = []
        self._print_and_save(self._generate_head(), self._html_array)
        self._print_and_save("<body>\n", self._html_array)

        start_time = self._database.control.get('start time', fallback=None)
        end_time = self._database.control.get('end time', fallback=None)
        date_string = ""
        if start_time:
            date_string = f"from {start_time} "
        if end_time:
            date_string = f"{date_string} until {end_time}"

        self._print_and_save(f"Exchanged {len(self._message_list):,} messages with {self._person} {date_string}<p>\n",
                             self._html_array)
        self._print_and_save(f'{" ":2s}<div class="picboxframe"  id="picbox"> <img src="" /> </div>\n',
                             self._html_array)

        self._html_array.append(self._generate_table(self._message_list))
        self._print_and_save('</body>\n</html>\n',
                             self._html_array)

    def __repr__(self) -> str:
        return ''.join(self._html_array)

    def save(self) -> None:
        """ Write the output to the output file"""
        print('\n'.join(self._html_array), file=self._output_file)
        return

    def print(self) -> None:
        """ Print the output to stdout """
        print('\n'.join(self._html_array))
        return

    def _print_and_save(self, message: str, array: list) -> None:
        """ Save to the output file while it is processing """
        array.append(message)
        if self._output_file:
            print(message, end="", file=self._output_file)

    def _generate_table(self, message_list: Messages) -> str:
        table_array = []
        self._print_and_save(f'{" ":2s}<table class="main_table">\n', table_array)

        previous_day = ''

        message_count = 0
        with alive_bar(len(message_list), title="Generating HTML", stats="({rate}, eta: {eta})") as bar:
            for message in message_list:
                message_count = message_count + 1

                today = message.date[:10]
                if today != previous_day:
                    previous_day = today

                    # If it's a new day, end the table, and start a new one
                    self._print_and_save(f'{" ":2s}</table>\n\n{" ":2s}<table class="main_table">\n', table_array)

                    self._day = datetime(int(message.date[0:4]), int(message.date[5:7]), int(message.date[8:10]),
                                         int(message.date[11:13]), int(message.date[14:16]),
                                         int(message.date[17:19])).strftime('%a')
                self._print_and_save(self._generate_row(message), table_array)
                if message.attachments:
                    bar()
                else:
                    bar(skipped=True)

        self._print_and_save(f'{" ":2s}</table>\n', table_array)
        return ''.join(table_array)

    def _generate_row(self, message: Message) -> str:
        # Specify if the message is from me, or the other person
        if message.is_from_me:
            who = self._me
            style = 'me'
        else:
            who = self._person
            style = 'them'

        # Check to see if we want the media box floating or fixed
        floating_option = self._database.config['DISPLAY'].get('popup location', fallback='floating')
        floating = floating_option == 'floating'

        # If this message is part of a thread, then show the messages in the thread before it
        thread_table = ""
        if message.thread_originator_guid:
            if message.thread_originator_guid in self._message_list.guids:
                original_message = self._message_list.guids[message.thread_originator_guid]
                thread_list = original_message.thread
                thread_list[original_message.rowid] = original_message
                print_thread = []
                # sort the threads by the date sent
                for i in sorted(thread_list.values(), key=lambda x: x.date):
                    if i == message: # stop at the current message
                        break
                    print_thread.append(i)
                thread_table = _generate_thread_table(print_thread, style)

        # Generate the attachment string
        attachments_string = ""
        if message.attachments:
            for attachment_key in message.attachments:
                if attachment_key not in self._attachment_list.attachment_list:
                    attachments_string = f'{attachments_string} <span class="missing"> Attachment missing </span> '
                    continue

                attachment = self._attachment_list.attachment_list[attachment_key]
                attachment_string = ""
                if attachment.skip:
                    continue
                if attachment.missing:
                    attachment_string = f'{attachments_string} <span class="missing"> Attachment missing </span> '
                    continue
                if attachment.copy:
                    if attachment.conversion_type == 'HEIC':
                        attachment.convert_heic_image(attachment.original_path, attachment.destination_path)
                    elif attachment.conversion_type == 'Audio' or attachment.conversion_type == 'Video':
                        attachment.convert_audio_video(attachment.original_path, attachment.destination_path)
                    else:
                        attachment.copy_attachment()

                if floating:
                    box_name = f'PopUp{attachment.rowid}'
                    image_box = f'<div class="imageBox" id="PopUp{attachment.rowid}">  <img src="" /> </div>'
                else:
                    box_name = 'picbox'
                    image_box = ''

                if attachment.popup_type == 'Picture':
                    if self._inline:
                        attachment_string = f'<p><a href="{attachment.html_path}" target="_blank">' \
                                            f'<img src="{attachment.html_path}" target="_blank"/><p>' \
                                            f' {attachment.html_path} </a>\n'
                    else:
                        attachment_string = f'''<a href="{attachment.html_path}" target="_blank"
            onMouseOver="ShowPicture('{box_name}',1,'{attachment.html_path}')" 
            onMouseOut="ShowPicture('{box_name}',0)"> {attachment.html_path} </a>
'''
                elif attachment.popup_type == 'Audio':
                    # Not going to do popups for audio, just inline
                    attachment_string = f'<p><audio controls>  <source src="{attachment.html_path}" ' \
                                        f'type="audio/mp3"></audio> <a href="{attachment.html_path}" ' \
                                        f'target="_blank"> {attachment.html_path} </a>\n'
                elif attachment.popup_type == 'Video':
                    if self._inline:
                        attachment_string = f'<p><video controls>  <source src="{attachment.html_path}" ' \
                                            f' type="video/mp4"></video> <p><a href="{attachment.html_path}"' \
                                            f' target="_blank"> {attachment.html_path} </a>\n'
                    else:
                        attachment_string = f'''<a href="{attachment.html_path}" target="_blank"
            onMouseOver="ShowMovie('{box_name}', 1, '{attachment.html_path}')"> {attachment.html_path} </a>
'''

                else:
                    attachment_string = f'<a href="{attachment.html_path}" target="_blank"> ' \
                                        f'{attachment.html_path} </a>\n'

                attachments_string = f'{attachments_string} <p> {attachment_string} {image_box} '

        # Structure of the text row. The first three columns are normal, the fourth column is complex
        #   <tr>
        #     <td> date
        #     <td> who
        #     <td>
        #       <table>
        #         <tr hidden>
        #           <td> Edited Row
        #         </tr>
        #         <tr>
        #           <td> Text of message (edited if required)
        #           <td hidden> extra text
        #           <td> info button (if configured)
        #         <tr>

        text = _replace_url_to_link(f'{message.text} {attachments_string}')

        # Check for edits on the text. If there are edits, then set up the html to allow for that. The row
        #   doesn't exist if there is no edits

        edited_string = ""
        edit_table = ""
        text_cell_edit_row = ""

        if len(message.edits) > 0:
            edit_table = f'{" ":14s}<div class="edits_{style}">\n'
            for i in range(0, len(message.edits)):
                edit_table = f'{edit_table}{" ":16s}"{message.edits[i]["text"]} <p>\n'
            edit_table = f'{edit_table}{" ":14s}</div>\n'
            edited_string = f'<sub><button class="edited_button"' \
                            f' onclick="ToggleDisplay(\'{message.rowid}editTable\')"> Edited </button></sub>'
            text_cell_edit_row = f'{" ":10s}<tr id={message.rowid}editTable class="edits">\n' \
                                 f'{" ":12s}<td>\n' \
                                 f'{edit_table} ' \
                                 f'{" ":12s}</td>\n ' \
                                 f'{" ":10s}</tr>\n'

        # Check for if we want additional data

        info_text = ""
        info_button = ""
        if self._database.control.getboolean('additional details', fallback=False):
            info_text = f'{" ":12s}<td class="infocell" id={message.rowid}info>\n ' \
                        f'{" ":14s}<table>\n' \
                        f'{" ":16s}<tr>\n' \
                        f'{" ":18s}<td> ChatID: {message.chat_id} </td>\n' \
                        f'{" ":16s}</tr>\n' \
                        f'{" ":14s}</table>\n' \
                        f'{" ":12s}</td>\n'
            info_button = f'{" ":12s}<td class="button-wrapper"> <button class="text_{style}" ' \
                          f'onclick="ToggleDisplay(\'{message.rowid}info\')"> ℹ️ </button> </td>\n'

        # Put together the row cells

        date_cell = f'{" ":6s}<td class="date"> {self._day} {message.date} </td>\n'
        name_cell = f'{" ":6s}<td class="name_{style}"> {who}: </td>\n'

        text_cell = f'{" ":6s}<td>\n ' \
                    f'{" ":8s}<table>\n' \
                    f'{text_cell_edit_row}' \
                    f'{" ":10s}<tr>\n' \
                    f'{" ":12s}<td class="text_{style}">\n' \
                    f'{thread_table}' \
                    f'{" ":14s}{text} {edited_string}\n' \
                    f'{" ":12s}</td>\n' \
                    f'{info_text}' \
                    f'{info_button}' \
                    f'{" ":10s}</tr>\n' \
                    f'{" ":8s}</table>\n' \
                    f'{" ":6s}</td>\n'

        row_string = f'{" ":4s}<tr id={message.rowid}>\n' \
                     f'{date_cell}' \
                     f'{name_cell}' \
                     f'{text_cell}' \
                     f'{" ":4s}</tr>\n'

        return row_string

    def _generate_head(self) -> str:
        popup = self._database.config['DISPLAY'].get('popup location', fallback='upper right')
        if popup == 'upper right':
            popup_location = 'right'
        else:
            popup_location = 'left'

        me_html_background_color = self._database.config['DISPLAY'].get('me html background_color',
                                                                        fallback='AliceBlue')
        them_html_background_color = self._database.config['DISPLAY'].get('them html background color',
                                                                          fallback='Lavender')
        thread_background_color = self._database.config['DISPLAY'].get('thread background',
                                                                       fallback='HoneyDew')
        me_thread_background_color = self._database.config['DISPLAY'].get('me thread background',
                                                                          fallback='AliceBlue')
        them_thread_background_color = self._database.config['DISPLAY'].get('them thread background',
                                                                            fallback='Lavender')
        me_html_name_color = self._database.config['DISPLAY'].get('me html name color',
                                                                  fallback='Blue')
        them_html_name_color = self._database.config['DISPLAY'].get('them html name color',
                                                                    fallback='Purple')

        css = '''    <style>
table {''' + f'''
    width: 100%;
    table-layout: auto;
''' + ''' }

table.main_table {''' + f'''
    border-bottom: 3px solid black;
    border-spacing: 8px;
''' + ''' }

table.thread_table_me {''' + f'''
    width: 50%;
    margin-right: 0px;
    margin-left: auto;
    background: {thread_background_color};
    padding: 5px;
    border-radius: 30px;
''' + ''' }

table.thread_table_them {''' + f'''
    width: 50%;
    margin-right: auto;
    margin-left: 0px;
    background: {thread_background_color};
    padding: 5px;
    border-radius: 30px;
''' + ''' }

td {''' + f'''
    padding: 0px;
    margin: 0;
    line-height: 1;
''' + ''' }

td.date {''' + f'''
    text-align: left;
    width: 150px;
    vertical-align: text-middle;
    font-size: 80%;
''' + ''' }

td.name_me {''' + f'''
    text-align: right;
    font-weight: bold;
    color: {me_html_name_color};
    width: 50px;
    padding-right: 5px;
    vertical-align: text-middle;
    font-size: 80%;
    
''' + ''' }

td.name_them {''' + f'''
    text-align: right;
    font-weight: bold;
    color: {them_html_name_color};
    width: 50px;
    padding-right: 5px;
    vertical-align: text-middle;
    font-size: 80%;
''' + ''' }

td.text_me {''' + f'''
    text-align: right;
    word-wrap: break-word;
    border-radius: 30px;
    padding: 15px;
    border-spacing: 40px;
    background: {me_html_background_color};  
''' + ''' }

td.text_them {''' + f'''
    text-align: left;
    word-wrap: break-word;
    border-radius: 30px;
    padding: 15px;
    border-spacing: 40px;
    background: {them_html_background_color};
''' + ''' }

.edits_me {''' + f'''
    display: none;
    font-size: 70%;
    font-style: italics;
    text-align: right;
    border-radius: 30px;
''' + ''' }  

.edits_them {''' + f'''
    display: none;
    font-size: 70%;
    font-style: italics;
    text-align: left;
    border-radius: 30px;
''' + ''' }    

.infocell {''' + f'''
    margin-right: 0px;
    margin-left: auto;
    width: 20%;
    text-align: right;
    font-size: 70%;
    display: none;
''' + ''' }

button.edited_button {''' + f'''
    font-size: 50%;
    border-radius: 30px;
    font-size: 50%;
    padding-left: 0px;
    padding-right: 0px;
    border-spacing: 0px;
    border-bottom: 0px;
    margin-right: 0px;
    margin-left: 0px;
    text-align: center;
    border: 0px;
    color: blue;
    font-style: italic;
    background-color: transparent;
''' + ''' }

td.button-wrapper {''' + f'''
    margin-right: 0px;
    margin-left: 4px;
    padding-left: 0px;
    padding-right: 0px;
    border-spacing: 0px;
    text-align: center;
    width:0.1%;
    background-color: transparent; 
''' + ''' }

button.text_me {''' + f'''
    background: {me_html_background_color};
    border-radius: 30px;
    font-size: 50%;
    padding-left: 0px;
    padding-right: 0px;
    border-spacing: 0px;
    border-bottom: 0px;
    margin-right: 0px;
    margin-left: 0px;
    text-align: center;
    border: 0px;
''' + ''' }

button.text_them {''' + f'''
    background: {them_html_background_color};
    border-radius: 30px;
    font-size: 50%;
    padding-left: 0px;
    padding-right: 0px;
    border-spacing: 0px;
    border-bottom: 0px;
    margin-right: 0px;
    margin-left: 0px;
    text-align: center;
    border: 0px;
''' + ''' }

reply_text_thread {''' + f'''
    border: 2px solid;
    background: {thread_background_color};
    border-radius: 6px;
    border-radius: 50px;
    font-size: 60%
''' + ''' }

.reply_text_me {''' + f'''
    border: 2px solid;
    background: {me_thread_background_color};
    border-radius: 6px;
    border-radius: 50px;
    font-size: 60%
''' + ''' }

.reply_text_them {''' + f'''
    border: 2px solid;
    background: {them_thread_background_color};
    border-radius: 6px;
    border-radius: 50px;
    font-size: 60%
''' + ''' }

td.blank {''' + f'''
    border: none;
    width: 50%
''' + ''' }

.missing {''' + f'''
    color: red;
''' + ''' }

.badjoin {''' + f'''
    color: red;
''' + ''' }

.imageBox {''' + f'''
    position: absolute;
    visibility: hidden;
    height: 200;
    border: solid 1px #CCC;
    padding: 5px;
''' + ''' }

img {''' + f'''
    height: 250px;
    width: auto;
''' + ''' }

.picboxframe {''' + f'''
    position: fixed;
    top: 2%;
    ''' + f'{popup_location}: 2%;' \
          '''
    background: Blue;
    transition: all .5s ease;

''' + ''' }

    </style>'''
        script = '''  <script>
    
    function ToggleDisplay(id) {
      if (document.getElementById(id).style.display == "none") {
          document.getElementById(id).style.display = "inline";
      }
      else {
          document.getElementById(id).style.display = "none";
      }
    }
    
    function ShowPicture(id,show, img) {
      if (show=="1") {
        document.getElementById(id).style.visibility = "visible"
        document.getElementById(id).childNodes[1].src = img;
      }
      else if (show=="0") {
        document.getElementById(id).style.visibility = "hidden"
      }
    }

    function ShowMovie(id, show, movie) {
        var elem = document.getElementById(id);
''' \
                 f'        var htmlstring = "<video controls onMouseOut=\'ShowMovie(\\\"\" + id + "\\\",0)\'> ' \
                 f'<source src=\'" + movie + "\'> </video>";' \
                 '''
        if (show == "1") {
          {
            elem.style.visibility = "visible";
            elem.innerHTML = htmlstring;
          }
        } else if (show == "0") {
          {
            elem.style.visibility = "hidden";
            elem.innerHTML =  " "
          }
        }
      }
  </script>'''

        head_string = '''<!DOCTYPE html>
<html lang="en-US">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    ''' \
                      f'    <title> {self._person} </title>\n{css}\n{script}\n</head>\n'
        return head_string
