
import imessagedb
import os


def test_connection():
    database = imessagedb.DB(os.path.join(os.path.dirname(__file__), "chat.db"))
    assert database
