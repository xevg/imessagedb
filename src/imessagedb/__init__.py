# read version from installed package
from importlib.metadata import version
__version__ = version("imessagedb")

from imessagedb.db import DB
from imessagedb.handle import Handle
from imessagedb.handles import Handles
from imessagedb.attachment import Attachment
from imessagedb.attachments import Attachments
from imessagedb.chat import Chat
from imessagedb.chats import Chats
from imessagedb.message import Message
from imessagedb.messages import Messages
from imessagedb.html import HTMLOutput

if __name__ == '__main__':

    print("iMessageDB successfully installed")
    # HOME_DIR = os.environ['HOME']
    # database = imessagedb.DB(f"{HOME_DIR}/Library/Messages/chat.db")