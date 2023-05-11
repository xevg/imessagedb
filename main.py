# This is a sample Python script.

import getopt
import logging
import configparser
import os
import sys
from datetime import datetime
from termcolor import colored

import imessagedb

translator_command = "/Users/xev/Dropbox/message_scripts/MessageTranslator/MessageTranslator/MessageTranslator"


def create_default_config(file_name):
    config = configparser.ConfigParser()
    config['DISPLAY'] = {
        'me_background_color': 'AliceBlue',
        'them_background_color': 'Lavender',
        'me_name': 'Blue',
        'them_name': 'Purple',
        'thread_background': 'HoneyDew',
        'me_thread': 'AliceBlue',
        'them_thread': 'Lavender',
    }
    with open(file_name, 'w') as configfile:
        config.write(configfile)
    return config


def Usage():
    print(
        f'{sys.argv[0]} --output_directory <dir> --name <name> --verbose --debug')
    sys.exit()


def print_handles(db):
    print(db.handles)
    return


def get_contacts(configuration):
    result = {}
    contact_list = configuration.items('CONTACTS')
    for contact in contact_list:
        key = contact[0]
        value = contact[1]
        stripped = value.replace('\n', '').replace(' ', '')
        number_list = stripped.split(',')
        result[key] = number_list
    return result


if __name__ == '__main__':

    HOME_DIR = os.environ['HOME']
    config_file = f'{HOME_DIR}/.config/iMessageDB.ini'
    create = False
    verbose = True
    debug = False
    no_table = False
    no_copy = False
    no_attachment = False
    inline = False
    output_directory = '/tmp'

    logging.basicConfig(level=logging.INFO, format='%(asctime)s <%(name)s> %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger('main')
    logger.info("Processing parameters")
    options, remainder = getopt.getopt(sys.argv[1:], 'ao:n:tvic', ['output_directory=',
                                                                   'verbose',
                                                                   'debug',
                                                                   'name=',
                                                                   'notable',
                                                                   'nocopy',
                                                                   'inline',
                                                                   'noattachment',
                                                                   'config'
                                                                   ])
    out = sys.stdout
    Person = None

    for opt, arg in options:
        if opt in ('-o', '--output_directory'):
            output_directory = arg
            create = True
        elif opt in ('-v', '--verbose'):
            verbose = True
        elif opt in ('-d', '--debug'):
            debug = True
        elif opt in ('-n', '--name'):
            Person = arg
        elif opt in ('-t', '--notable'):
            no_table = True
        elif opt in ('-i', '--inline'):
            inline = True
        elif opt in ('c', '--nocopy'):
            no_copy = True
        elif opt in ('a', '--noattachment'):
            no_attachment = True
        elif opt in '--config':
            config_file = arg

    logger.debug(f'OPTIONS   : {options}')
    if not os.path.exists(config_file):
        config = create_default_config(config_file)
    else:
        config = configparser.ConfigParser()
        config.read(config_file)

    preface = ''

    contacts = get_contacts(config)

    if not Person:
        logger.error('You have to specify who you want to search')
        Usage()

    if Person.lower() not in contacts.keys():
        logger.error(f"{Person} not known. Please edit contacts list.")
        Usage()

    output_directory = output_directory
    config['CONTROL']['attachment directory'] = f"{output_directory}/{Person}_attachments"

    if create:
        logger.info("Preparing output locations")
        filename = f'{Person}.html'
        out = open(f'{output_directory}/{filename}', 'w')
        attachments_path_stripped = f"{Person}_attachments"
        try:
            os.mkdir(config['CONTROL']['attachment directory'])
        except FileExistsError:
            pass

    database = imessagedb.DB(f"{HOME_DIR}/Library/Messages/chat.db", config=config)
    message_list = database.Messages(Person, contacts[Person.lower()])

    logger.info("Outputting messages ...")
    database.TextOutput('Xev', Person, message_list, database.attachment_list, output_file=out).print()
    # print(text_string)
    html_string = database.HTMLOutput('Xev', Person, message_list, database.attachment_list, output_file=out)

    print("The end")
    database.disconnect()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
