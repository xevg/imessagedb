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
    expected_path = f"{os.environ['HOME']}/Library/Messages/Attachments/4f/15/D7CEBAED-9844-4B25-B841-F7748EA3BCAD/IMG_4911.heic"
    assert attachment.original_path == expected_path, "Unexpected value in attachment"
