# read version from installed package
from importlib.metadata import version
__version__ = version("imessagedb")

from imessagedb.db import DB

if __name__ == '__main__':

    print("iMessageDB successfully installed")
    # HOME_DIR = os.environ['HOME']
    # database = DB(f"{HOME_DIR}/Library/Messages/chat.db")
