from datetime import datetime
import re
import string
import imessagedb
from imessagedb.message import Message
from imessagedb.messages import Messages
from alive_progress import alive_bar

url_pattern = re.compile(r'((https?):((//)|(\\\\))+[\w\d:#@%/;$()~_?+-=\\.&]*)', re.MULTILINE | re.UNICODE)
mailto_pattern = re.compile(r'([\w\-.]+@(\w[\w\-]+\.)+[\w\-]+)', re.MULTILINE | re.UNICODE)


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
                that the attachments are stored, so it cannot display them 2) Some attachments need
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

    html background color list = AliceBlue, Cyan, Gold, Lavender, LightGreen, PeachPuff, Wheat
    html name color list = Blue, DarkCyan, DarkGoldenRod, Purple, DarkGreen, Orange, Sienna :
        The background and name color of the messages in html output
        The options for colors can be found here: https://www.w3schools.com/cssref/css_colors.php

        The way that the color selection works is that it will use the first color on the color list for the
        first person in the conversation, the second for the second, third for the third, etc. If there are more
        participants than colors, it will wrap around to the first color.

    thread background = HoneyDew :
        The background color of the thread in replies
    """

    def __init__(self, database, me: str, messages: Messages, inline: bool = False, output_file: str = None) -> None:
        """
            Parameters
            ----------
            database : imessagedb.DB
                An instance of a connected database

            me : str
                Your display name

            messages: imessagedb.DB.Messages
                 The messages

            inline : bool
                Display attachments inline or not

            output_file : str
                The name of the output file"""

        self._database = database
        self._me = me
        self._messages = messages
        self._attachment_list = self._database.attachment_list
        self._inline = inline

        self._name_map = {}
        self._color_list = self._get_next_color()
        self._day = 'UNK'
        self._html_array = []
        self._current_messages_processed = 0
        self._current_messages_file = 0
        self._file_start_date: datetime = None
        self._file_end_date: datetime = None
        self._previous_range: str = None
        self._last_row_had_conversion = False

        if output_file is not None:
            self._output_filename = output_file
            self._split_output = self._database.config.getint('DISPLAY', 'split output', fallback=0)
            self._previous_output_filename = None
            self._current_output_filename = f"{self._output_filename}.html"
            self._output_file_handle = open(self._current_output_filename, "w")
        else:
            self._output_filename = None

        start_time = self._database.control.get('start time', fallback=None)
        end_time = self._database.control.get('end time', fallback=None)
        date_string = ""
        if start_time:
            date_string = f" from {start_time}"
        if end_time:
            date_string = f"{date_string} until {end_time}"

        self._file_header_string = f'  <div id="file_summary">Exchanged {len(self._messages):,} total messages with ' \
                                   f'{self._messages.title}{date_string}.</div><p>\n'

        self._html_array.append(self._generate_table(self._messages))
        self._print_and_save('</body>\n</html>\n', self._html_array, eof=True)

    def __repr__(self) -> str:
        return ''.join(self._html_array)

    def save(self, filename: str) -> None:
        """ Write the output to the output file"""
        file_handle = open(filename, "w")
        print('\n'.join(self._html_array), file=file_handle)
        file_handle.close()
        return

    def print(self) -> None:
        """ Print the output to stdout """
        print('\n'.join(self._html_array))
        return

    def _print_and_save(self, message: str, array: list, new_day: bool = False, eof: bool = False) -> None:
        """ Save to the output file while it is processing """

        if self._current_messages_processed == 0:
            # If this is a new file, because it is either the first pass through, or if we need to create new file

            new_file_array = [self._generate_head(), "<body>\n", self._file_header_string,
                              f'{" ":2s}<div class="picboxframe"  id="picbox"> <img src="" /> </div>\n',
                              f'{" ":2s}<table style="table-layout: fixed;">\n{" ":4s}<tr>\n']
            if self._previous_output_filename:
                new_file_array.append(f'{" ":6s}<td style="text-align: left; width: 33%;">'
                                      f'<a href="file://{self._previous_output_filename}"> &lt </a> </td>\n'
                                      f'{" ":6s}<td style="text-align: center; width: 33%;"><div class="next_file">' +
                                      f'<a href="file://{self._previous_output_filename}">' +
                                      f' Previous Messages {self._previous_range}</a></div></td>\n')
            else:
                new_file_array.append(f'{" ":6s}<td style="width: 33%;"> </td>\n'
                                      f'{" ":6s}<td style="width: 33%;"> </td>\n')

            new_file_array.append(f'{" ":6s}<td style="text-align: right; width: 33%;" id="next_page"> </td>\n'
                                  f'{" ":4s}</tr>\n{" ":2s}</table>\n\n')
            new_file_array.append(f'{" ":2s}<table class="main_table">\n{" ":2s}</table>\n')

            for i in new_file_array:
                array.append(i)
                if self._output_filename is not None:
                    print(i, end="", file=self._output_file_handle)

        array.append(message)
        self._current_messages_processed += 1
        if self._output_filename is None:  # We are not writing to a file
            return

        if eof:
            # Normally this gets done on the file split, but the eof indicates its last file, so do it
            #  on the last write

            description_string = f' This page contains {self._current_messages_processed:,} messages from ' \
                                 f'{self._file_start_date.strftime("%A %Y-%m-%d")} to ' \
                                 f'{self._file_end_date.strftime("%A %Y-%m-%d")}.'
            print(f' <script>\n'
                  f'  el = document.getElementById("file_summary")\n'
                  f'  new_text = el.innerHTML.concat("{description_string}")\n'
                  f'  el.innerHTML = new_text\n',
                  f' </script>\n', file=self._output_file_handle)

        print(message, end="", file=self._output_file_handle)

        if new_day and 0 < self._split_output < self._current_messages_processed:
            total_processed = self._current_messages_processed
            self._current_messages_processed = 0
            self._current_messages_file += 1
            self._previous_output_filename = self._current_output_filename
            self._current_output_filename = f"{self._output_filename}_{self._current_messages_file:02d}.html"

            print(f'    <p><div class="next_file"><a href="file://{self._current_output_filename}">'
                  f' Next Messages </a></div>\n', end="", file=self._output_file_handle)
            description_string = f' This page contains {total_processed:,} messages from ' \
                                 f'{self._file_start_date.strftime("%A %Y-%m-%d")} to ' \
                                 f'{self._file_end_date.strftime("%A %Y-%m-%d")}.'
            self._previous_range = f'<br><div style="font-size: 50%;">' \
                                   f'({self._file_start_date.strftime("%A %Y-%m-%d")} to ' \
                                   f'{self._file_end_date.strftime("%A %Y-%m-%d")})</div>'
            print(f' <script>\n'
                  f'  el = document.getElementById("file_summary")\n'
                  f'  new_text = el.innerHTML.concat("{description_string}")\n'
                  f'  el.innerHTML = new_text\n'
                  f'  document.getElementById("next_page").innerHTML = '
                  f'   "<a href=\'file://{self._current_output_filename}\'> Next Page &gt </a>"\n'
                  f' </script>', file=self._output_file_handle)
            print('</body>\n</html>\n', end="", file=self._output_file_handle)
            self._output_file_handle.close()
            print(f"Creating output file {self._current_output_filename}")
            self._output_file_handle = open(self._current_output_filename, "w")

    def _generate_thread_row(self, message: Message) -> str:
        if message.is_from_me:
            who_data = self._get_name(0)
        else:
            who_data = self._get_name(message.handle_id)
        style = who_data['style']

        text = message.text
        row_string = f'{" ":16s}<tr>\n' \
                     f'{" ":18s}<td class="reply_name" style="color: {who_data["name_color"]};"> ' \
                     f'{who_data["name"]}: </td>\n' \
                     f'{" ":18s}<td class="reply_text_thread">\n' \
                     f'{" ":20s}<a href="#{message.rowid}">\n' \
                     f'{" ":22s}<button class="reply_text_{style}" style="background: ' \
                     f'{who_data["background_color"]};"> ' \
                     f'{text}</button>\n' \
                     f'{" ":20s}</a>\n' \
                     f'{" ":18s}</td>\n' \
                     f'{" ":16s}</tr>\n'
        return row_string

    def _generate_thread_table(self, message_list: list, style: str) -> str:
        table_string = f'{" ":14s}<table class="thread_table_{style}">\n'
        for message in message_list:
            table_string = f'{table_string}{self._generate_thread_row(message)}'
        table_string = f'{table_string}' \
                       f'{" ":14s}</table>\n' \
                       f'{" ":14s}<p>\n'
        return table_string

    def _generate_table(self, message_list: Messages) -> str:
        table_array = []
        self._print_and_save(f'{" ":2s}<table class="main_table">\n', table_array)

        previous_day = ''

        message_count = 0
        with alive_bar(len(message_list), title="Generating HTML", stats="({rate}, eta: {eta})", comma=True) as bar:
            for message in message_list:
                message_count = message_count + 1

                today = message.date[:10]
                if today != previous_day:
                    previous_day = today

                    message_date = datetime(int(message.date[0:4]), int(message.date[5:7]), int(message.date[8:10]),
                                            int(message.date[11:13]), int(message.date[14:16]),
                                            int(message.date[17:19]))

                    if self._file_start_date is None:
                        self._file_start_date = message_date
                    self._file_end_date = message_date

                    # If it's a new day, end the table, and start a new one
                    self._print_and_save(f'{" ":2s}</table>\n\n', table_array, new_day=True)
                    self._print_and_save(f'{" ":2s}<table class="main_table">\n', table_array)

                    self._day = message_date.strftime('%a')
                self._last_row_had_conversion = False
                self._print_and_save(self._generate_row(message), table_array)
                if self._last_row_had_conversion:
                    bar()
                else:
                    bar(skipped=True)

        self._print_and_save(f'{" ":2s}</table>\n', table_array)
        return ''.join(table_array)

    def _get_next_color(self):
        """ A generator function to return the next color"""

        counter = -1
        default_background_color_list = 'AliceBlue, Cyan, Gold, Lavender, LightGreen, PeachPuff, Wheat'
        default_name_color_list = 'Blue, DarkCyan, DarkGoldenRod, Purple, DarkGreen, Orange, Sienna'
        background_color_list = self._database.config.get('DISPLAY', 'html background color list',
                                                          fallback=default_background_color_list)
        name_color_list = self._database.config.get('DISPLAY', 'html name color list',
                                                    fallback=default_name_color_list)

        background_colors = background_color_list.translate({ord(c): None for c in string.whitespace}).split(',')
        name_colors = name_color_list.translate({ord(c): None for c in string.whitespace}).split(',')

        while True:
            counter += 1
            next_background_color = counter % len(background_colors)
            next_name_color = counter % len(name_colors)

            yield [background_colors[next_background_color], name_colors[next_name_color]]

    def _get_name(self, handle_id: str) -> dict:
        if handle_id not in self._name_map:
            (background_color, name_color) = next(self._color_list)
            handle_list = self._database.handles.handles
            if handle_id == 0:  # 0 is me
                self._name_map[handle_id] = {'name': self._me, 'background_color': background_color,
                                             'name_color': name_color, 'style': 'me'}
            elif handle_id in handle_list:
                handle = handle_list[handle_id]
                self._name_map[handle_id] = {'name': handle.name, 'background_color': background_color,
                                             'name_color': name_color, 'style': 'them'}
            else:
                self._name_map[handle_id] = {'name': handle_id, 'background_color': background_color,
                                             'name_color': name_color, 'style': 'them'}

        return self._name_map[handle_id]

    def _generate_row(self, message: Message) -> str:
        # Specify if the message is from me, or the other person
        if message.is_from_me:
            who_data = self._get_name(0)
        else:
            who_data = self._get_name(message.handle_id)
        who = who_data['name']
        style = who_data['style']

        # Check to see if we want the media box floating or fixed
        floating_option = self._database.config['DISPLAY'].get('popup location', fallback='floating')
        floating = floating_option == 'floating'

        # If this message is part of a thread, then show the messages in the thread before it
        thread_table = ""
        if message.thread_originator_guid:
            if message.thread_originator_guid in self._messages.guids:
                original_message = self._messages.guids[message.thread_originator_guid]
                thread_list = original_message.thread
                thread_list[original_message.rowid] = original_message
                print_thread = []
                # sort the threads by the date sent
                for i in sorted(thread_list.values(), key=lambda x: x.date):
                    if i == message:  # stop at the current message
                        break
                    print_thread.append(i)
                thread_table = self._generate_thread_table(print_thread, style)

        # Generate the attachment string
        attachments_string = ""
        if message.attachments:
            for attachment_key in message.attachments:
                # If the attachment listed does not exist, then just list is as missing and continue to the next one
                if attachment_key not in self._attachment_list.attachment_list:
                    attachments_string = f'{attachments_string} <span class="missing"> Attachment missing </span> '
                    continue

                attachment = self._attachment_list.attachment_list[attachment_key]
                # If the attachment exists, but we have it marked to skip, skip it
                if attachment.skip:
                    continue

                # If the attachment exists, but is marked as missing, list it as missing and continue
                if attachment.missing:
                    attachments_string = f'{attachments_string} <span class="missing"> Attachment missing </span> '
                    continue

                # If we should copy the attachment, copy it or convert it
                if attachment.copy:
                    if attachment.conversion_type == 'HEIC':
                        attachment.convert_heic_image(attachment.original_path, attachment.destination_path)
                        self._last_row_had_conversion = True
                    elif attachment.conversion_type == 'Audio' or attachment.conversion_type == 'Video':
                        attachment.convert_audio_video(attachment.original_path, attachment.destination_path)
                        self._last_row_had_conversion = True
                    else:
                        attachment.copy_attachment()
                        self._last_row_had_conversion = True

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
        name_cell = f'{" ":6s}<td class="name_{style}" style="color: {who_data["name_color"]};"> {who}: </td>\n'

        text_cell = f'{" ":6s}<td>\n ' \
                    f'{" ":8s}<table>\n' \
                    f'{text_cell_edit_row}' \
                    f'{" ":10s}<tr>\n' \
                    f'{" ":12s}<td class="text_{style}" style="background: {who_data["background_color"]};">\n' \
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

        thread_background_color = self._database.config['DISPLAY'].get('thread background',
                                                                       fallback='HoneyDew')

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
    width: 50px;
    padding-right: 5px;
    vertical-align: text-middle;
    font-size: 80%;
    
''' + ''' }

td.name_them {''' + f'''
    text-align: right;
    font-weight: bold;
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
''' + ''' }

td.text_them {''' + f'''
    text-align: left;
    word-wrap: break-word;
    border-radius: 30px;
    padding: 15px;
    border-spacing: 40px;
''' + ''' }

.edits_me {''' + f'''
    display: none;
    font-size: 70%;
    font-style: italic;
    text-align: right;
    border-radius: 30px;
''' + ''' }  

.edits_them {''' + f'''
    display: none;
    font-size: 70%;
    font-style: italic;
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

.reply_name {
    font-size: 50%; 
    text-align: right;
}

.reply_text_me {''' + f'''
    border: 2px solid;
    border-radius: 6px;
    border-radius: 50px;
    font-size: 60%
''' + ''' }

.reply_text_them {''' + f'''
    border: 2px solid;
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

.next_file {
    text-align: center;
    font-size: 150%;
}

#file_summary {
    font-style: italic;
}

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
                      f'    <title> {self._messages.title} </title>\n{css}\n{script}\n</head>\n'
        return head_string
