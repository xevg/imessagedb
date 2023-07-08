from termcolor import colored
from datetime import datetime
import string


class TextOutput:
    """ Creates a text file (or string) from a Messages list

        ...

        There are a number of options in the configuration file that affect how the HTML is created.
        In the DISPLAY section, the following impact the output:

         me = Me :
                    The name to put for your part of the conversation. It defaults to 'Me'.

        use text color = True :
                    If False, don't color the text at all

        text color list = red, green, yellow, blue, magenta, cyan
                    The color for the name in text output. No color is used if 'use text color' is false.
                    The color can only be one of the following options:
                        black, red, green, yellow, blue, magenta, cyan, white, light_grey, dark_grey,
                        light_red, light_green, light_yellow, light_blue, light_magenta, light_cyan

                    The way that the color selection works is that it will use the first color on the color list
                    for the first person in the conversation, the second for the second, third for the third, etc.
                    If there are more participants than colors, it will wrap around to the first color.


        reply text color = light_grey :
                    The color for the reply text """

    def __init__(self, database, me: str, messages, output_file=None) -> None:
        self._database = database
        self._me = me
        self._messages = messages
        self._attachment_list = self._database.attachment_list
        self._output_file = output_file
        self._color_list = self._get_next_color()
        self._name_map = {}

        self._use_color = self._database.config['DISPLAY'].getboolean('use text color', fallback=True)
        self._me_color = self._database.config['DISPLAY'].get('me text color', fallback="blue")
        self._them_color = self._database.config['DISPLAY'].get('them text color', fallback="magenta")
        self._reply_color = self._database.config['DISPLAY'].get('reply text color', fallback="light_grey")

        start_time = self._database.control.get('start time', fallback=None)
        end_time = self._database.control.get('end time', fallback=None)
        date_string = ""
        if start_time:
            date_string = f"from {start_time} "
        if end_time:
            date_string = f"{date_string} until {end_time}"

        header_string = f"Exchanged {len(self._messages.message_list):,} messages with " \
                        f"{self._messages.title} {date_string}"
        self._string_array = [header_string]
        self._get_messages()
        return

    def _get_name(self, handle_id: str) -> dict:
        if handle_id not in self._name_map:
            color = next(self._color_list)
            handle_list = self._database.handles.handles
            if handle_id == 0:  # 0 is me
                self._name_map[handle_id] = {'name': self._me, 'color': color}
            elif handle_id in handle_list:
                handle = handle_list[handle_id]
                self._name_map[handle_id] = {'name': handle.name, 'color': color}
            else:
                self._name_map[handle_id] = {'name': handle_id, 'color': color}

        return self._name_map[handle_id]

    def _print_thread(self, thread_header, current_message: str) -> str:
        thread_string = ""
        thread_list = thread_header.thread
        thread_list[thread_header.rowid] = thread_header
        for i in sorted(thread_list.values(), key=lambda x: x.date):
            if i == current_message:
                break
            attachment_string = ""
            if i.attachments is not None:
                attachment_string = f" Attachments: {i.attachments}"
            thread_string = f'{thread_string}[{self._name_map[i.handle_id]["name"]}: {i.text}{attachment_string}] '
        return thread_string

    def _get_messages(self) -> None:
        for message in self._messages.message_list:
            date = message.date

            day = datetime(int(date[0:4]), int(date[5:7]), int(date[8:10]),
                           int(date[11:13]), int(date[14:16]),
                           int(date[17:19])).strftime('%a')

            if message.is_from_me:
                who_data = self._get_name(0)
            else:
                who_data = self._get_name(message.handle_id)
            who = self._color(who_data['name'], who_data['color'], attrs=['bold'])

            reply_to = ""
            attachment_string = ""

            if message.attachments:
                attachments_array = []
                attachment_list = self._database.attachment_list.attachment_list
                for i in message.attachments:
                    if i in attachment_list:
                        attachments_array.append(attachment_list[i].original_path)
                    else:
                        attachments_array.append(f"Missing attachment ({i})")

                attachment_string = f'Attachments: {",".join(attachments_array)}'
            if message.thread_originator_guid:
                if message.thread_originator_guid in self._messages.guids:
                    original_message = self._messages.guids[message.thread_originator_guid]
                    reply_to = self._color(f'Reply to: {self._print_thread(original_message, message)}',
                                           self._reply_color)
            self._string_array.append(f'<{day} {date}> {who}: {message.text} {reply_to} {attachment_string}')

    def _get_next_color(self):
        """ A generator function to return the next color"""

        counter = -1
        color_list = self._database.config.get('DISPLAY', 'text color list',
                                               fallback='red, green, yellow, blue, magenta, cyan')
        colors = color_list.translate({ord(c): None for c in string.whitespace}).split(',')
        while True:
            counter += 1
            yield colors[counter % len(colors)]

    def _color(self, text: str, color: str, attrs=None) -> str:
        if self._use_color:
            if attrs:
                return colored(text, color, attrs=attrs)
            else:
                return colored(text, color)
        else:
            return text

    def save(self) -> None:
        """ Save the text output to the file """
        print('\n'.join(self._string_array), file=self._output_file)
        return

    def print(self) -> None:
        """ Print the text output to stdout """
        print('\n'.join(self._string_array))
        return

    def __repr__(self) -> str:
        return '\n'.join(self._string_array)
