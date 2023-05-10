
class Chat:
    def __init__(self, database, rowid, chat_identifier, chat_name, last_message_date=None):
        self._database = database
        self._rowid = rowid
        self._chat_identifier = chat_identifier
        self._chat_name = chat_name
        self._last_message_date = last_message_date
        self._participants = []

    def __repr__(self):
        return f'{self.rowid}: id => {self.chat_identifier} name => "{self.chat_name}" ' \
               f'last_message => {self.last_message_date}, participants => "{self.participants}"'

    @property
    def rowid(self):
        return self._rowid

    @property
    def chat_identifier(self):
        return self._chat_identifier

    @property
    def chat_name(self):
        return self._chat_name

    @property
    def last_message_date(self):
        return self._last_message_date

    @last_message_date.setter
    def last_message_date(self, date):
        self._last_message_date = date

    @property
    def participants(self):
        strings = []
        for handle_id in self._participants:
            if handle_id in self._database.handles.handles:
                strings.append(f'{self._database.handles.handles[handle_id].number} ({handle_id})')
            else:
                strings.append(f'{handle_id}')
        return ', '.join(strings)

    def add_participant(self, participant):
        if participant not in self._participants:
            self._participants.append(participant)

