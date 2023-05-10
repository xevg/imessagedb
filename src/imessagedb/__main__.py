

import imessagedb
import os

if __name__ == '__main__':

    print("iMessageDB installed")
    HOME_DIR = os.environ['HOME']
    database = imessagedb.DB(f"{HOME_DIR}/Library/Messages/chat.db")
