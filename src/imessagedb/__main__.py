

import imessagedb
import os


def print_handles(db):
    print(db.handles)
    return


def get_contacts(configuration):
    result = {}
    contact_list = configuration.items('CONTACTS')
    for contact in contact_list:
        key = contact[0]
        value = contact[1]

        # Get rid of spaces and newlines
        stripped = value.replace('\n', '').replace(' ', '')
        number_list = stripped.split(',')
        result[key] = number_list
    return result


if __name__ == '__main__':

    print("iMessageDB installed")
    HOME_DIR = os.environ['HOME']
    database = imessagedb.DB(f"{HOME_DIR}/Library/Messages/chat.db")
