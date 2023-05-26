import plistlib
from datetime import datetime

from imessagedb.utils import *
import imessagedb


def _convert_attributed_body(encoded: bytes) -> str:
    # This general logic was copied from
    # https://github.com/my-other-github-account/imessage_tools/blob/master/imessage_tools.py, however
    # I needed to make some improvements

    text = encoded.split(b'NSNumber')[0]
    text = text.split(b'NSString')[1]
    text = text.split(b'NSDictionary')[0]
    text = text[6:-12]
    if b'\x01' in text:
        text = text.split(b'\x01')[1]
    if b'\x02' in text:
        text = text.split(b'\x02')[1]
    if b'\x00' in text:
        text = text.split(b'\x00')[1]
    if b'\x86' in text:
        text = text.split(b'\x86')[0]
    return text.decode('utf-8', errors='replace')


class Message:
    """ Class for holding information about a message """

    def __init__(self, database, rowid: int, guid: str, date: str, is_from_me: bool, handle_id: str,
                 attributed_body: bytes, message_summary_info: bytes, text: str, reply_to_guid: str,
                 thread_originator_guid: str, thread_originator_part: str, chat_id: str, message_attachments: list):
        """
                Parameters
                ----------
                database : imessagedb.DB
                    An instance of a connected database

                rowid, guid, date, is_from_me, handle_id, attributed_body, message_summary_info, text,
                 reply_to_guid, thread_originator_guid, thread_originator_part, chat_id : str
                    The parameters are the fields in the database

                message_attachments : list
                    The attachments for this message"""

        self._rowid = rowid
        self._guid = guid
        self._date = date
        self._is_from_me = is_from_me
        self._handle_id = handle_id
        self._attributed_body = attributed_body
        self._message_summary_info = message_summary_info
        self._text = text
        self._attributed_body = attributed_body
        self._reply_to_guid = reply_to_guid
        self._thread_originator_guid = thread_originator_guid
        self._thread_originator_part = thread_originator_part
        self._chat_id = chat_id
        self._attachments = message_attachments
        self._thread = {}
        self._edits = []

        # There are a lot of messages that are saved into attributed_body instead of the text field.
        #  There isn't a good way to convert this in Python that I've found, so I have to run a
        #  program to do it. I need to fix this.

        if (self._text is None or text == '' or text == ' ') and self._attributed_body is not None:
            self._text = _convert_attributed_body(self._attributed_body)

        # Edits are stored in message_summary_info
        try:
            plist = plistlib.loads(self._message_summary_info)
            if 'ec' in plist:
                for row in plist['ec']['0']:
                    self._edits.append({'text': _convert_attributed_body(row['t']),
                                        'date': convert_from_database_date(row['d'])})
        except plistlib.InvalidFileException as exp:
            pass

    def __repr__(self) -> str:
        return_string = f'RowID: {self._rowid}' \
                        f' GUID: {self._guid}' \
                        f' Date: {self._date}' \
                        f' From me: {self._is_from_me}' \
                        f' HandleID: {self._handle_id}' \
                        f' Message: {self._text}' \
                        f' Originator Thread: {self._thread_originator_guid}' \
                        f' Reply Message: {self._reply_to_guid}' \
                        f' Thread Part: {self._thread_originator_part}' \
                        f' Chat ID: {self._chat_id}' \
                        f' Attachments: {self._attachments}'
        return str(return_string)

    @property
    def rowid(self) -> int:
        return self._rowid

    @property
    def guid(self) -> str:
        return self._guid

    @property
    def date(self) -> str:
        return self._date

    @property
    def is_from_me(self) -> bool:
        return self._is_from_me

    @property
    def handle_id(self) -> str:
        return self._handle_id

    @property
    def attributed_body(self) -> bytes:
        return self._attributed_body

    @property
    def message_summary_info(self) -> bytes:
        return self._message_summary_info

    @property
    def text(self) -> str:
        return self._text

    @property
    def edits(self) -> list:
        return self._edits

    @property
    def reply_to_guid(self) -> str:
        return self._reply_to_guid

    @property
    def thread_originator_guid(self) -> str:
        return self._thread_originator_guid

    @property
    def chat_id(self) -> str:
        return self._chat_id

    @property
    def attachments(self) -> list:
        return self._attachments

    @property
    def thread(self) -> dict:
        return self._thread
