# from db import DB
# from handle import Handle
# from handles import Handles
# from attachment import Attachment
# from attachments import Attachments
# from chat import Chat
# from chats import Chats
# from message import Message
# from messages import Messages
# from html import HTMLOutput

import imessagedb
import os

if __name__ == '__main__':

    HOME_DIR = os.environ['HOME']
    database = imessagedb.DB(f"{HOME_DIR}/Library/Messages/chat.db")
