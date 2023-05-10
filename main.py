# This is a sample Python script.

import getopt
import logging
import configparser
import os
import sys
from datetime import datetime

import imessagedb

translator_command = "/Users/xev/Dropbox/message_scripts/MessageTranslator/MessageTranslator/MessageTranslator"

contacts = {
    'Ashley': ['+18484676050', 'ashleywilliams_@live.com', 'sparkette325@yahoo.com', '+17325722108',
               'williaa2@kean.edu'],
    'Abe': ['+16103499696'],
    'Alisha': ['+15082088327'],
    'Emily': ['+12672803303'],
    'Hermosa': ['+17329103453'],
    'Kanani': ['+17325351530'],
    'Randi': ['+16093394399'],
    'Rose': ['fhecla@gmail.com', '+16109602522'],
    'Marta': ['+19172974204'],
    'Maxine': ['mlee99@optonline.net', 'panda9966@gmail.com', '+19084725929', '+17323816580'],
    'Monika': ['+19176678993', 'mnowak2@binghamton.edu', 'Xplsumnerx@gmail.com'],
    'Michele': ['+12153917169'],
    'Marissa': ['+14016490739'],
    'Lily': ['lilyyalexb@gmail.com', 'njlibrn@yahoo.com', '+17327887245'],
    'Daniel': ['daniel@gittler.com', '+17326460220', 'dsg1002@gmail.com', 'gittlerd@gmail.com', 'dgittler@berklee.edu'],
    'Kandela': ['+17324849684'],
    'Tiffany': ['Wickedblueglow@gmail.com', 'Tlgreenberg80@gmail.com', '+17327105145'],
    'Jessica': ['jessica.marozine@icloud.com', 'jessica.marozine@gmail.com', '+17326923688'],
    'Becky': ['rebecca@schore.org', '+17329838356'],
    'Lynda': ['lylasmith559@yahoo.com', 'lylalombardi@icloud.com', '+17323001586'],
    'Stefanie': ['stefanie.thomas2@gmail.com', 'thostefa@kean.edu', '+17326101065'],
}


def print_thread(thread_header, current_message):
    thread_string = ""
    thread_list = thread_header.thread
    thread_list[thread_header.rowid] = thread_header
    for i in sorted(thread_list.values(), key=lambda x: x.date):
        if i == current_message:
            break
        attachment_string = ""
        if i.attachment_list is not None:
            attachment_string = f" Attachments: {i.attachment_list}"
        thread_string = f'{thread_string}[{i.text}{attachment_string}] '
    return thread_string


def print_messages(name, message_list):

    for message in message_list.message_list:
        # (rowid, date, is_me, handle_id, attributedBody, text, attachment) = message
        date = message.date

        day = datetime(int(date[0:4]), int(date[5:7]), int(date[8:10]),
                       int(date[11:13]), int(date[14:16]),
                       int(date[17:19])).strftime('%a')

        if message.is_from_me:
            # who = BOLD + 'Xev' + END
            who = 'Xev'
        else:
            # who  = BOLD + person + END
            who = name

        reply_to = ""
        attachment_string = ""

        if message.attachment_list:
            attachment_string = f'Attachments: {message.attachment_list}'
        if message.thread_originator_guid:
            if message.thread_originator_guid in message_list.guids:
                original_message = message_list.guids[message.thread_originator_guid]
                reply_to = print_thread(original_message, message)
                # if original_message.text is not None:
                #    reply_to = f'Reply To: {original_message.text}'
                #     if original_message.attachments is not None:
                #        reply_to = f'{reply_to} Attachments: {original_message.attachments}'
        print(f'<{day} {date}> {message.rowid} {who}: {message.text} {reply_to} {attachment_string}', flush=True)


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

    database = imessagedb.DB(f"{HOME_DIR}/Library/Messages/chat.db")
    # chats = chats.Chats(database)

    if not Person:
        logger.error('You have to specify who you want to search')
        Usage()

    if Person not in contacts.keys():
        logger.error(f"{Person} not known. Please edit contacts list.")
        Usage()

    if create:
        logger.info("Preparing output locations")
        filename = f'{Person}.html'
        out = open(f'{output_directory}/{filename}', 'w')
        attachments_path = f'{output_directory}/{Person}_attachments'
        attachments_path_stripped = f"{Person}_attachments"
        try:
            os.mkdir(attachments_path)
        except FileExistsError:
            pass

    logger.info("Getting attachments")
    attachment_list = imessagedb.Attachments(database, copy=True, copy_directory=attachments_path)

    logger.info("Getting messages")
    message_list = imessagedb.Messages(database, Person, contacts[Person], attachment_list)

    logger.info("Outputting messages ...")
    html_string = imessagedb.HTMLOutput('Xev', Person, contacts[Person], message_list, attachment_list, output_file=out)
    print(html_string, file=out)

#    handle_list = handles.Handles(database)
#    chat_list = chats.Chats(database)
    print("The end")
    database.disconnect()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
