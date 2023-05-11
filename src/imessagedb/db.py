import sqlite3
import os
import configparser
from imessagedb.attachments import Attachments
from imessagedb.messages import Messages
from imessagedb.chats import Chats
from imessagedb.handles import Handles
from imessagedb.html import HTMLOutput
from imessagedb.text import TextOutput


def _get_default_configuration():
    """Generates a default configuration if one is not passed in

    """

    config = configparser.ConfigParser()
    config['DISPLAY'] = {
        'me_background_color': 'AliceBlue',
        'them_background_color': 'Lavender',
        'me_name': 'Blue',
        'them_name': 'Purple',
        'thread_background': 'HoneyDew',
        'me_thread': 'AliceBlue',
        'them_thread': 'Lavender',
    }

    return config


class DB:
    """
    A class to connect to an iMessage database

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
    def __init__(self, database_name=f"{os.environ['HOME']}/Library/Messages/chat.db", config=None):
        """
        Parameters
        ----------
        database_name : str
            The database that it connects to (the default is to use the default database in the caller's home directory)

        config : ConfigParser
            Configuration information
        """

        self._database_name = database_name
        self._configuration = config

        if self._configuration is None:
            self._configuration = _get_default_configuration()

        self._control = self._configuration['CONTROL']

        self._chat_connection = sqlite3.connect(database_name)
        self._cursor = self._chat_connection.cursor()

        # Preload some of the data
        self._handles = Handles(self)
        self._chats = Chats(self)
        self._attachment_list = Attachments(self)
        return

    def Messages(self, person, numbers):
        """A wrapper to create a Messages class
        """
        return Messages(self, person, numbers)

    def HTMLOutput(self, me, person, message_list, attachment_list, inline=False, output_file=None):
        """A wrapper to create an HTMLOutput class
        """
        return HTMLOutput(self, me, person, message_list, attachment_list, inline, output_file)

    def TextOutput(self, me, person, message_list, attachment_list, output_file=None):
        """A wrapper to create a TextOutput class
        """
        return TextOutput(self, me, person, message_list, output_file)

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

    @property
    def attachment_list(self):
        """Returns an imessagedb.Attachments class with all the attachments
        """
        return self._attachment_list

    @property
    def config(self):
        """Returns the configuration object
        """
        return self._configuration

    @property
    def control(self):
        """Returns a shortcut to the CONTROL section of the configuration
                """
        return self._control
