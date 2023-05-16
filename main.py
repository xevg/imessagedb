# This is a sample Python script.

import argparse
import logging
import configparser
import os
import sys


import imessagedb


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

    config_file = f'{os.environ["HOME"]}/.config/iMessageDB.ini'
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

    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--name", help="Person to get conversations about", required=True)
    argument_parser.add_argument("-c", "--configfile", help="Location of the configuration file",
                                 default=f'{os.environ["HOME"]}/.config/iMessageDB.ini')
    argument_parser.add_argument("-o", "--output_directory",
                                 help="The output directory where the output and attachments go")
    argument_parser.add_argument("--database", help="The database file to open",
                                 default=f"{os.environ['HOME']}/Library/Messages/chat.db")
    argument_parser.add_argument("-m", "--me", help="The name to use to refer to you", default="Me")
    argument_parser.add_argument("-t", "--output_type", help="The type of output", choices=["text", "html"])
    argument_parser.add_argument("-i", "--inline", help="Show the attachments inline", action="store_true")
    mutex_group = argument_parser.add_mutually_exclusive_group()
    mutex_group.add_argument("-f", "--force", help="Force a copy of the attachments", action="store_true")
    mutex_group.add_argument("--no_copy", help="Don't copy the attachments", action="store_true")
    argument_parser.add_argument("--no_attachments", help="Don't process attachments at all", action="store_true")
    argument_parser.add_argument("-v", "--verbose", help="Turn on additional output", action="store_true")


    args = argument_parser.parse_args()

    # First read in the configuration file, creating it if need be, then overwrite the values from the command line
    if not os.path.exists(args.configfile):
        imessagedb._create_default_configuration(args.configfile)
    config = configparser.ConfigParser()
    config.read(args.configfile)

    CONTROL = 'CONTROL'
    DISPLAY = 'DISPLAY'

    config.set(CONTROL, 'Person', args.name)
    config.set(CONTROL, 'verbose', str(args.verbose))
    if args.output_directory:
        config.set(CONTROL, 'copy directory', args.output_directory)
    if args.no_copy:
        config.set(CONTROL, 'copy', 'False')
    if args.output_type:
        config.set(CONTROL, 'output type', args.output_type)
    if args.force:
        config.set(CONTROL, 'force copy', 'True')
    if args.no_attachments:
        config.set(CONTROL, 'skip attachments', 'True')
    if args.inline:
        config.set(DISPLAY, 'inline attachments', 'True')

    out = sys.stdout

    contacts = get_contacts(config)
    Person = config[CONTROL]['Person']
    if Person.lower() not in contacts.keys():
        logger.error(f"{Person} not known. Please edit contacts list.")
        Usage()

    config[CONTROL]['attachment directory'] = f"{config[CONTROL]['copy directory']}/{Person}_attachments"

    filename = f'{Person}.html'
    out = open(f"{config[CONTROL]['copy directory']}/{filename}", 'w')
    try:
        os.mkdir(config['CONTROL']['attachment directory'])
    except FileExistsError:
        pass

    database = imessagedb.DB(args.database, config=config)
    message_list = database.Messages(Person, contacts[Person.lower()])

    # database.TextOutput(args.me, Person, message_list, output_file=out).print()
    html_string = database.HTMLOutput(args.me, Person, message_list, output_file=out)

    print("The end")
    database.disconnect()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
