from termcolor import colored
from datetime import datetime
import imessagedb


def _print_thread(thread_header, current_message: str) -> str:
    thread_string = ""
    thread_list = thread_header.thread
    thread_list[thread_header.rowid] = thread_header
    for i in sorted(thread_list.values(), key=lambda x: x.date):
        if i == current_message:
            break
        attachment_string = ""
        if i.attachments is not None:
            attachment_string = f" Attachments: {i.attachments}"
        thread_string = f'{thread_string}[{i.text}{attachment_string}] '
    return thread_string


class TextOutput:
    """ Creates a text file (or string) from a Messages list

        ...

        There are a number of options in the configuration file that affect how the HTML is created.
        In the DISPLAY section, the following impact the output:

         me = Me :
                    The name to put for your part of the conversation. It defaults to 'Me'.

        use text color = True :
                    If False, don't color the text at all

        me text color = blue
        them text color = magenta :
                    The color for the names in text output. The color can only be one of the following options:
                    black, red, green, yellow, blue, magenta, cyan, white, light_grey, dark_grey,
                    light_red, light_green, light_yellow, light_blue, light_magenta, light_cyan

        reply text color = light_grey :
                    The color for the reply text """

    def __init__(self, database, me: str, person: str, messages, output_file=None) -> None:
        self._database = database
        self._me = me
        self._person = person
        self._messages = messages
        self._attachment_list = self._database.attachment_list
        self._output_file = output_file

        self._use_color = self._database.config['DISPLAY'].getboolean('use text color', fallback=True)
        self._me_color = self._database.config['DISPLAY'].get('me text color', fallback="blue")
        self._them_color = self._database.config['DISPLAY'].get('them text color', fallback="magenta")
        self._reply_color = self._database.config['DISPLAY'].get('reply text color', fallback="light_grey")

        self._string_array = []
        self._get_messages()
        return

    def _get_messages(self) -> None:
        for message in self._messages.message_list:
            date = message.date

            day = datetime(int(date[0:4]), int(date[5:7]), int(date[8:10]),
                           int(date[11:13]), int(date[14:16]),
                           int(date[17:19])).strftime('%a')

            if message.is_from_me:
                who = self._color(self._me, self._me_color, attrs=['bold'])
            else:
                who = self._color(self._person, self._them_color, attrs=['bold'])

            reply_to = ""
            attachment_string = ""

            if message.attachments:
                attachment_string = f'Attachments: {message.attachments}'
            if message.thread_originator_guid:
                if message.thread_originator_guid in self._messages.guids:
                    original_message = self._messages.guids[message.thread_originator_guid]
                    reply_to = self._color(f'Reply to: {_print_thread(original_message, message)}',
                                           self._reply_color)
            self._string_array.append(f'<{day} {date}> {who}: {message.text} {reply_to} {attachment_string}')

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
