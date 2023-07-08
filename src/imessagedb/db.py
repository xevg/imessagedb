import configparser
import os
import sqlite3

import imessagedb
from imessagedb.attachments import Attachments
from imessagedb.chats import Chats
from imessagedb.handles import Handles
from imessagedb.generate_html import HTMLOutput
from imessagedb.messages import Messages
from imessagedb.generate_text import TextOutput


class DB:
    """
    A class to connect to an iMessage database

    """
    def __init__(self, database_name=None, config=None):
        """
        Parameters
        ----------
        database_name : str
            The database that it connects to (the default is to use the default database in the caller's home directory)

        config : ConfigParser
            Configuration information. If none is provided, we will create a default.
        """

        if database_name is None:
            database_name = f"{os.environ['HOME']}/Library/Messages/chat.db"
        self._database_name = database_name
        self._configuration = config

        if self._configuration is None:
            self._configuration = configparser.ConfigParser()
            self._configuration.read_string(imessagedb.DEFAULT_CONFIGURATION)

        self._control = self._configuration['CONTROL']

        self._chat_connection = sqlite3.connect(database_name)
        self._cursor = self._chat_connection.cursor()

        # Preload some of the data
        self._handles = Handles(self)
        self._chats = Chats(self)
        self._attachment_list = Attachments(self)
        return

    def Messages(self, query_type: str, title: str, numbers: list = None, chat_id: str = None) -> Messages:
        """A wrapper to create a Messages class
        """
        return Messages(self, query_type, title, numbers=numbers, chat_id=chat_id)

    def HTMLOutput(self, me: str, message_list: Messages, inline=False, output_file=None) -> HTMLOutput:
        """A wrapper to create an HTMLOutput class
        """
        return HTMLOutput(self, me, message_list, inline, output_file)

    def TextOutput(self, me: str, message_list: Messages, output_file=None) -> TextOutput:
        """A wrapper to create a TextOutput class
        """
        return TextOutput(self, me, message_list, output_file)

    def disconnect(self) -> None:
        """Disconnects from the database

        """
        self._chat_connection.close()
        return

    @property
    def connection(self) -> sqlite3.Cursor:
        """Returns a connection to query the database
        """
        return self._cursor

    @property
    def handles(self) -> Handles:
        """Returns an imessagedb.Handles class with all the handles
        """
        return self._handles

    @property
    def chats(self) -> Chats:
        """Returns an imessagedb.Chats class with all the chats
        """
        return self._chats

    @property
    def attachment_list(self) -> Attachments:
        """Returns an imessagedb.Attachments class with all the attachments
        """
        return self._attachment_list

    @property
    def config(self) -> configparser.ConfigParser:
        """Returns the configuration object
        """
        return self._configuration

    @property
    def control(self):
        """Returns a shortcut to the CONTROL section of the configuration
                """
        return self._control
