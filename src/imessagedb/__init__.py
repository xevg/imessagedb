"""
Provides access to the iMessage chat.db, including parsing and output

"""
from importlib.metadata import version

# read version from installed package

__version__ = version("imessagedb")

import os
import configparser
import logging
import argparse
import sys
from datetime import datetime
from imessagedb.db import DB


DEFAULT_CONFIGURATION = '''
[CONTROL]

# Whether or not to copy the attachments into a different directory. This is needed for two reasons:
#  1) The web browser does not have access to the directory that the attachments are stored, so it cannot display them
#  2) Some of the attachments need to be converted in order to be viewed in the browser

copy = True

# The directory to put the output. The html file will go in {copy_directory}/{Person}.html,
#   and the attachments will go in {copy_directory}/{Person}_Attachments

copy directory = /tmp

# If the file already exists in the destination directory it is not recopied, but that can be overridden by
#  specifying 'force copy' as true

force copy = False

# 'Skip attachments' ignores attachments

skip attachments = False

# Additional details show some other information on each message, including the chat id and any edits that have 
#  been done

additional details = False

# Some extra verbosity if true

verbose = True

[DISPLAY]

# Output type, either html or text

output_type = html

# Inline attachments mean that the images are in the HTML instead of loaded when hovered over

inline attachments = False

# Popup location is where the attachment popup window shows up, and is either 'upper right', 'upper left' or 'floating'

popup location = upper right

# 'me' is the name to put for your text messages
me = Me

# The color for the name in text output. No color is used if 'use text color' is false.
#  The color can only be one of the following options:
#   black, red, green, yellow, blue, magenta, cyan, white, light_grey, dark_grey,
#   light_red, light_green, light_yellow, light_blue, light_magenta, light_cyan

use text color = True
me text color = blue
them text color = magenta
reply text color = light_grey

# The background color of the text messages for you and for the other person in html output
# The options for colors can be found here: https://www.w3schools.com/cssref/css_colors.php

me html background color = AliceBlue
them html background color = Lavender

# The background color of the thread in replies

thread background = HoneyDew
me thread background = AliceBlue
them thread background = Lavender

# The color of the name in the html output

me html name color = Blue
them html name color = Purple


[CONTACTS]

# A person that you text with can have multiple numbers, and you may not always want to specify the full specific
#  number as stored in the handle database, so you can do the mapping here, providing the name of a person,
#  and a comma separated list of numbers

Samantha: +18434676040, samanthasmilt@gmail.com, 
   s12ddd2@colt.edu
Abe: +16103499696
Marissa: +14029490739
'''


def _create_default_configuration(filename: str) -> None:
    """Generates a default configuration if one is not passed in

    """

    f = open(filename, "w")
    f.write(DEFAULT_CONFIGURATION)
    f.close()
    return


def get_contacts(configuration: configparser.ConfigParser) -> dict:
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


def run() -> None:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s <%(name)s> %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger('main')
    logger.debug("Processing parameters")

    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('--handle', help="A list of handles to search against", nargs='*')
    argument_parser.add_argument("--name", help="Person to get conversations about")
    argument_parser.add_argument("-c", "--configfile", help="Location of the configuration file",
                                 default=f'{os.environ["HOME"]}/.config/iMessageDB.ini')
    argument_parser.add_argument("-o", "--output_directory",
                                 help="The output directory where the output and attachments go")
    argument_parser.add_argument("--database", help="The database file to open",
                                 default=f"{os.environ['HOME']}/Library/Messages/chat.db")
    argument_parser.add_argument("-m", "--me", help="The name to use to refer to you", default="Me")
    argument_parser.add_argument("-t", "--output_type", help="The type of output", choices=["text", "html"])
    argument_parser.add_argument("-i", "--inline", help="Show the attachments inline", action="store_true")
    copy_mutex_group = argument_parser.add_mutually_exclusive_group()
    copy_mutex_group.add_argument("-f", "--force", help="Force a copy of the attachments", action="store_true")
    copy_mutex_group.add_argument("--no_copy", help="Don't copy the attachments", action="store_true")
    argument_parser.add_argument("--no_attachments", help="Don't process attachments at all", action="store_true")
    argument_parser.add_argument("-v", "--verbose", help="Turn on additional output", action="store_true")
    argument_parser.add_argument('--start_time', help="The start time of the messages in YYYY-MM-DD HH:MM:SS format")
    argument_parser.add_argument('--end_time', help="The end time of the messages in YYYY-MM-DD HH:MM:SS format")
    argument_parser.add_argument('--version', help="Prints the version number", action="store_true")
    argument_parser.add_argument('--get_handles', '--get-handles',
                                 help="Display the list of handles in the database and exit", action="store_true")
    argument_parser.add_argument('--get_chats', '--get-chats',
                                 help="Display the list of chats in the database and exit", action="store_true")

    args = argument_parser.parse_args()

    if args.version:
        print(f"imessagedb {__version__}", file=sys.stderr)
        exit(0)

    # First read in the configuration file, creating it if need be, then overwrite the values from the command line
    if not os.path.exists(args.configfile):
        _create_default_configuration(args.configfile)
    config = configparser.ConfigParser()
    config.read(args.configfile)

    CONTROL = 'CONTROL'
    DISPLAY = 'DISPLAY'

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

    start_date = None
    end_date = None
    if args.start_time:
        try:
            start_date = datetime.strptime(args.start_time, '%Y-%m-%d %H:%M:%S')
        except ValueError as exp:
            argument_parser.print_help(sys.stderr)
            print(f"\n **Start time not correct: {exp}", file=sys.stderr)
            exit(1)
        config.set(CONTROL, 'start time', str(start_date))
    if args.end_time:
        try:
            end_date = datetime.strptime(args.end_time, '%Y-%m-%d %H:%M:%S')
        except ValueError as exp:
            argument_parser.print_help(sys.stderr)
            print(f"\n** End time not correct: {exp}", file=sys.stderr)
            exit(1)
        config.set(CONTROL, 'end time', str(end_date))
    if start_date and end_date and start_date >= end_date:
        argument_parser.print_help(sys.stderr)
        print(f"\n **Start date ({start_date}) must be before end date ({end_date})", file=sys.stderr)
        exit(1)

    generic_database_request = False
    if args.get_handles or args.get_chats:
        config[CONTROL]['skip attachments'] = 'True'
        generic_database_request = True

    if not generic_database_request:

        person = None
        numbers = None

        if args.handle:
            numbers = args.handle
            if args.name:
                person = args.name
            else:
                person = ', '.join(numbers)
        elif args.name:
            person = args.name
            contacts = get_contacts(config)
            if person.lower() not in contacts.keys():
                logger.error(f"{person} not known. Please edit your contacts list.")
                argument_parser.print_help()
                exit(1)
            # Get rid of new lines and split it into a list
            numbers = config['CONTACTS'][person].replace('\n', '').split(',')
        else:
            argument_parser.print_help(sys.stderr)
            print("\n ** You must supply either a name or one or more handles")
            exit(1)

        config.set(CONTROL, 'Person', person)

    # Connect to the database

    database = DB(args.database, config=config)

    if args.get_handles:
        print(f"Available handles in the database:\n{database.handles.get_handles()}")
        sys.exit(0)

    if args.get_chats:
        print(f"Available chats in the database:\n{database.chats.get_chats()}")
        sys.exit(0)

    out = sys.stdout

    copy_directory = config[CONTROL].get('copy directory', fallback="/tmp")
    attachment_directory = f"{copy_directory}/{person}_attachments"
    config[CONTROL]['attachment directory'] = attachment_directory

    filename = f'{person}.html'
    out = open(f"{copy_directory}/{filename}", 'w')
    try:
        os.mkdir(attachment_directory)
    except FileExistsError:
        pass

    # TODO: Implement functions to display a chat, given a chat_name or chat_id

    message_list = database.Messages(person, numbers)
    output_type = config[CONTROL].get('output type', fallback='html')
    if output_type == 'text':
        database.TextOutput(args.me, person, message_list, output_file=out).print()
    else:
        database.HTMLOutput(args.me, person, message_list, output_file=out)

    database.disconnect()


if __name__ == '__main__':
    run()
