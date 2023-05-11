
import imessagedb
import os


def test_connection():
    database = imessagedb.DB(f"{os.environ['HOME']}/Library/Messages/chat.db")
    assert database
