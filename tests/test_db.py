import configparser

import imessagedb
import os


def test_connection():
    database = imessagedb.DB(os.path.join(os.path.dirname(__file__), "chat.db"))
    assert database


def test_configuration():
    database = imessagedb.DB(os.path.join(os.path.dirname(__file__), "chat.db"))
    config = database.config
    assert isinstance(config, configparser.ConfigParser), \
        "Expected return of database.config to be of class 'configparser.ConfigParser'"
    assert config['CONTROL'], "Expected the CONTROL section to be in the configuration"
