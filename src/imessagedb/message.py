class Message:
    def __init__(self, rowid, guid, date, is_from_me, handle_id, attributed_body, text,
                 reply_to_guid, thread_originator_guid, thread_originator_part, chat_id, attachments):
        self._rowid = rowid
        self._guid = guid
        self._date = date
        self._is_from_me = is_from_me
        self._handle_id = handle_id
        self._attributed_body = attributed_body
        self._text = text
        self._reply_to_guid = reply_to_guid
        self._thread_originator_guid = thread_originator_guid
        self._thread_originator_part = thread_originator_part
        self._chat_id = chat_id
        self._attachments = attachments
        self._thread = {}

    def __repr__(self):
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
    def rowid(self):
        return self._rowid

    @property
    def guid(self):
       return self._guid

    @property
    def date(self):
        return self._date

    @property
    def is_from_me(self):
        return self._is_from_me

    @property
    def handle_id(self):
        return self._handle_id

    @property
    def attributed_body(self):
        return self._attributed_body

    @property
    def text(self):
        return self._text

    @property
    def reply_to_guid(self):
        return self._reply_to_guid

    @property
    def thread_originator_guid(self):
        return self._thread_originator_guid

    @property
    def chat_id(self):
        return self._chat_id

    @property
    def attachments(self):
        return self._attachments

    @property
    def thread(self):
        return self._thread
