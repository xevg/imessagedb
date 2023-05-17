import imessagedb
import os


def test_handles():
    database = imessagedb.DB(os.path.join(os.path.dirname(__file__), "chat.db"))

    assert len(database.handles) == 2, "Unexpected number of handles"


def test_handle():
    database = imessagedb.DB(os.path.join(os.path.dirname(__file__), "chat.db"))
    h = database.handles
    hand = h.handles[2]
    assert hand.number == "scripting@schore.org", "Unexpected handle"
