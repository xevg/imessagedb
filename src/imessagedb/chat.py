from datetime import datetime


class Chat:
    """ Class for holding information about a chat """

    def __init__(self, database, rowid: str, chat_identifier: str, chat_name: str,
                 last_message_date=None) -> None:
        """
            Parameters
            ----------
            database : imessagedb.DB
                An instance of a connected database

            rowid, chat_identifier, chat_name : str
                The parameters are the fields in the database

            last_message_date : date
                The date the last message in this chat was sent"""

        self._database = database
        self._rowid = rowid
        self._chat_identifier = chat_identifier
        self._chat_name = chat_name
        self._last_message_date = last_message_date
        self._participants = []

    def __repr__(self) -> str:
        return f'{self.rowid}: id => {self.chat_identifier} name => "{self.chat_name}" ' \
               f'last_message => {self.last_message_date}, participants => "{self.participants}"'

    @property
    def rowid(self) -> str:
        return self._rowid

    @property
    def chat_identifier(self) -> str:
        return self._chat_identifier

    @property
    def chat_name(self) -> str:
        return self._chat_name

    @property
    def last_message_date(self) -> datetime:
        return self._last_message_date

    @last_message_date.setter
    def last_message_date(self, date: datetime):
        self._last_message_date = date

    @property
    def participants(self) -> str:
        """ Returns the participants in the chat """
        strings = []
        for handle_id in self._participants:
            if handle_id in self._database.handles.handles:
                number = self._database.handles.handles[handle_id].number
                name = self._database.handles.name_for_number(number)
                if name is None:
                    strings.append(f'{number} ({handle_id})')
                else:
                    strings.append(f'{name} ({number}):({handle_id})')
            else:
                strings.append(f'{handle_id}')
        return ', '.join(strings)

    def add_participant(self, participant: str):
        """ Add a participant to the chat """
        if participant not in self._participants:
            self._participants.append(participant)
