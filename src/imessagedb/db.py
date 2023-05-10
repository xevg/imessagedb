import sqlite3
import imessagedb
import os


class DB:
    """
    A class to connect to an iMessage databaes

    ...

    Attributes
    ---------
    handles : imessagedb.Handles
        A class that contains all the handles in the database
    chats : imessagedb.Chats
        A class that contains all the chats in the database
    connection : sqlite3.Cursor
        Used for reading directly from the database

    Methods
    ------
    disconnect()
        Disconnects from the database

    """
    def __init__(self, database_name=f"{os.environ['HOME']}/Library/Messages/chat.db"):
        """
        Parameters
        ----------
        database_name : str
            The database that it connects to (the default is to use the default database in the caller's home directory
        """

        self._database_name = database_name
        self._chat_connection = sqlite3.connect(database_name)
        self._cursor = self._chat_connection.cursor()

        # Preload some of the data
        self._handles = imessagedb.Handles(self)
        self._chats = imessagedb.Chats(self)
        return

    def disconnect(self):
        """Disconnects from the database

        """
        self._chat_connection.close()
        return

    @property
    def connection(self):
        return self._cursor

    @property
    def handles(self):
        return self._handles

    @property
    def chats(self):
        """Returns an imessagedb.Chats class with all the chats
        """
        return self._chats

