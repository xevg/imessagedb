
import imessagedb


def test_connection():
    database = imessagedb.DB("tests/chat.db")
    assert database
