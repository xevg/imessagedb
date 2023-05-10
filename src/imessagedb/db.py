import sqlite3
import imessagedb


class DB:
    def __init__(self, database_name):
        self._database_name = database_name
        self._chat_connection = sqlite3.connect(database_name)
        self._cursor = self._chat_connection.cursor()

        # Preload some of the data
        self._handles = iMessageDB.Handles(self)
        self._chats = iMessageDB.Chats(self)

    def disconnect(self):
        self._chat_connection.close()

    @property
    def cursor(self):
        return self._cursor

    @property
    def handles(self):
        return self._handles

    @property
    def chats(self):
        return self._chats

