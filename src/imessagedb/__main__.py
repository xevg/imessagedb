

import imessagedb
import os
import configparser
import logging
import argparse
import sys


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


def run():
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
    person = config[CONTROL]['Person']
    if person.lower() not in contacts.keys():
        logger.error(f"{person} not known. Please edit contacts list.")
        argument_parser.print_help()
        exit(1)

    config[CONTROL]['attachment directory'] = f"{config[CONTROL]['copy directory']}/{person}_attachments"

    filename = f'{person}.html'
    out = open(f"{config[CONTROL]['copy directory']}/{filename}", 'w')
    try:
        os.mkdir(config['CONTROL']['attachment directory'])
    except FileExistsError:
        pass

    database = imessagedb.DB(args.database, config=config)
    message_list = database.Messages(person, contacts[person.lower()])

    if config[CONTROL]['output type'] == 'text':
        database.TextOutput(args.me, person, message_list, database.attachment_list, output_file=out).print()
    else:
        database.HTMLOutput(args.me, person, message_list, database.attachment_list, output_file=out)

    print("The end")
    database.disconnect()


if __name__ == '__main__':
    imessagedb.run()

