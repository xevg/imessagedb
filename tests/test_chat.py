import imessagedb
import os


def test_chats():
    database = imessagedb.DB(os.path.join(os.path.dirname(__file__), "chat.db"))

    assert len(database.chats) == 2, "Unexpected number of chats"
