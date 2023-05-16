from datetime import datetime
import re
from alive_progress import alive_bar


def _generate_thread_row(message):
    if message.is_from_me:
        style = 'me'
    else:
        style = 'them'

    text = message.text
    # row_string = f'    <tr><td class="blank></td><td class="reply_text_{style}" > {text} </td ></tr>\n'
    row_string = f'    <tr>' \
                 f'      <td class="reply_text_{style}">\n' \
                 f'        <a href="#{message.rowid}">\n' \
                 f'          <button class="reply_text_{style}"> {text}</button>\n' \
                 f'        </a>\n' \
                 f'      </td>\n' \
                 f'    </tr>\n'
    return row_string


def _generate_thread_table(message_list, style):
    table_string = f'  <table class="thread_table_{style}">\n'
    for message in message_list:
        table_string = f'{table_string}{_generate_thread_row(message)}'
    table_string = f'{table_string}  </table>\n<p>\n'
    return table_string


def _replace_url_to_link(value):
    """ From https://gist.github.com/guillaumepiot/4539986 """

    # Replace url to link
    urls = re.compile(r"((https?):((//)|(\\\\))+[\w\d:#@%/;$()~_?\+-=\\\.&]*)", re.MULTILINE | re.UNICODE)
    value = urls.sub(r'<a href="\1" target="_blank">\1</a>', value)
    # Replace email to mailto
    urls = re.compile(r"([\w\-\.]+@(\w[\w\-]+\.)+[\w\-]+)", re.MULTILINE | re.UNICODE)
    value = urls.sub(r'<a href="mailto:\1">\1</a>', value)
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
    def __init__(self, database, me: str, person: str, message_list,
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
        self._print_and_save(f"Got {len(self._message_list):,} messages with {self._person}<p>\n",
                             self._html_array)
        self._print_and_save('<div class="picboxframe"  id="picbox"> <img src="" /> </div>',
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
            print(message, file=self._output_file)

    def _generate_table(self, message_list) -> str:
        table_array = []
        self._print_and_save('  <table class="main_table">\n', table_array)

        previous_day = ''

        message_count = 0
        with alive_bar(len(message_list), title="Generating HTML", stats="({rate}, eta: {eta})") as bar:
            for message in message_list:
                message_count = message_count + 1

                today = message.date[:10]
                if today != previous_day:
                    previous_day = today

                    # If it's a new day, end the table, and start a new one
                    self._print_and_save('</table>\n  <table class="main_table">\n', table_array)

                    self._day = datetime(int(message.date[0:4]), int(message.date[5:7]), int(message.date[8:10]),
                                         int(message.date[11:13]), int(message.date[14:16]),
                                         int(message.date[17:19])).strftime('%a')
                self._print_and_save(self._generate_row(message), table_array)
                if message.attachments:
                    bar()
                else:
                    bar(skipped=True)

        self._print_and_save('</table>\n', table_array)
        return ''.join(table_array)

    def _generate_row(self, message) -> str:
        if message.is_from_me:
            who = self._me
            style = 'me'
        else:
            who = self._person
            style = 'them'

        floating = self._database.config['DISPLAY']['popup location'] == 'floating'

        thread_table = ""
        if message.thread_originator_guid:
            if message.thread_originator_guid in self._message_list.guids:
                original_message = self._message_list.guids[message.thread_originator_guid]
                thread_list = original_message.thread
                thread_list[original_message.rowid] = original_message
                print_thread = []
                for i in sorted(thread_list.values(), key=lambda x: x.date):
                    if i == message:
                        break
                    print_thread.append(i)
                thread_table = _generate_thread_table(print_thread, style)

        attachments_string = ""
        if message.attachments:
            for attachment_key in message.attachments:
                if attachment_key not in self._attachment_list.attachment_list:
                    attachment_strings = f'{attachments_string} <span class="missing"> Attachment missing </span> '
                    continue

                attachment = self._attachment_list.attachment_list[attachment_key]
                attachment_string = ""
                if attachment.skip:
                    continue
                if attachment.missing:
                    attachment_strings = f'{attachments_string} <span class="missing"> Attachment missing </span> '
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

        text = _replace_url_to_link(f'{message.text} {attachments_string}')
        row_string = f'    <tr id={message.rowid}>\n' \
                     f'      <td class="date"> {self._day} {message.date} </td>\n' \
                     f'      <td class="name_{style}"> {who}: </td>\n' \
                     f'      <td class="text_{style}"> {thread_table} {text} </td >\n' \
                     f'    </tr>\n'
        return row_string

    def _generate_head(self) -> str:
        if self._database.config['DISPLAY']['popup location'] == 'upper right':
            popup_location = 'right'
        else:
            popup_location = 'left'

        css = '''    <style>
table {
    width: 100%;
    table-layout: auto;
}

table.main_table {
    border-bottom: 3px solid black;
    border-spacing: 8px;
}

table.thread_table_me {
    width: 50%;
    margin-right: 0px;
    margin-left: auto;
    background: honeydew;
    padding: 10px;
    border-radius: 30px;
}

table.thread_table_them {
    width: 50%;
    margin-right: auto;
    margin-left: 0px;
    background: honeydew;
    padding: 10px;
    border-radius: 30px;
}

td {
    padding: 0px;
    margin: 0;
    line-height : 1;
}
td.date {
    text-align: left;
    width: 150px;
    vertical-align: text-middle;
    font-size: 80%;
}

td.name_me {
    text-align: right;
    font-weight: bold;
    color: blue;
    width: 50px;
    padding-right: 5px;
    vertical-align: text-middle;
    font-size: 80%;
    
}

td.name_them {
    text-align: right;
    font-weight: bold;
    color: Purple;
    width: 50px;
    padding-right: 5px;
    vertical-align: text-middle;
    font-size: 80%;
    }

td.text_me {
    text-align: right;
    word-wrap: break-word;
    border-radius: 30px;
    padding: 15px;
    border-spacing: 50px;
    background: AliceBlue;  
}

td.text_them {
    text-align: left;
    word-wrap: break-word;
    background: Lavender;
    border-radius: 30px;
    padding: 15px;
}

.reply_text_me {
    border: 2px solid AliceBlue;
    background: AliceBlue;
    border-radius: 6px;
    border-radius: 50px;
    font-size: 60%
}

.reply_text_them {
    border: 2px solid Lavender;
    background: Lavender;
    border-radius: 6px;
    border-radius: 50px;
    font-size: 60%
}

td.blank {
    border: none;
    width: 50%
}

.missing {
    color: red;
}

.badjoin {
    color: red;
}

.imageBox {
    position: absolute;
    visibility: hidden;
    height: 200;
    border: solid 1px #CCC;
    padding: 5px;
}

img {
    height: 250px;
    width: auto;
}

.picboxframe {
    position: fixed;
    top: 2%;
    ''' + f'{popup_location}: 2%' \
              '''
    background: Blue;
    transition: all .5s ease;

  }

    </style>'''
        script = '''  <script>
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
                      f'    <title> {self._person} </title>\n{css}\n{script}\n</head>'
        return head_string
