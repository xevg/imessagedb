import imessagedb
import os


def test_attachments():
    database = imessagedb.DB(os.path.join(os.path.dirname(__file__), "chat.db"))

    attachments = database.attachment_list
    assert len(attachments.attachment_list) == 2, "Unexpected number of attachments"


def test_attachment():
    database = imessagedb.DB(os.path.join(os.path.dirname(__file__), "chat.db"))

    attachments = database.attachment_list
    attachment = attachments.attachment_list[98368]
    assert attachment.original_path == '/Users/xev/Library/Messages/Attachments/4f/15/D7CEBAED-9844-4B25-B841-F7748EA3BCAD/IMG_4911.heic', \
        "Unexpected value in attachment"
