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
import dateutil.parser
from imessagedb.db import DB
from imessagedb.utils import *

DEFAULT_CONFIGURATION = '''
[CONTROL]

# Whether or not to copy the attachments into a different directory. This is needed for two reasons:
#  1) The web browser does not have access to the directory that the attachments are stored, so it cannot display them
#  2) Some of the attachments need to be converted in order to be viewed in the browser

copy = True

# The directory to put the output. The html file will go in {copy_directory}/{Person}.html,
#   and the attachments will go in {copy_directory}/{Person}_Attachments. If you specify HOME, then
#   it will put it in your home directory

copy directory = HOME

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

output type = html

# Number of messages in each html file. If this is 0 or not specified, it will be one large file.
#  There may be more messages than this per file, as it splits at the next date change after that number 
#  of messages. 

split output = 1000

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

# The way that the color selection works is that it will use the first color on the color list for the first person
#  in the conversation, the second for the second, third for the third, etc. If there are more participants than colors,
#  it will wrap around to the first color.

use text color = True
text color list = red, green, yellow, blue, magenta, cyan
reply text color = light_grey

# The background and name color of the messages in html output
# The options for colors can be found here: https://www.w3schools.com/cssref/css_colors.php

# The way that the color selection works is that it will use the first color on the color list for the first person
#  in the conversation, the second for the second, third for the third, etc. If there are more participants than colors,
#  it will wrap around to the first color.

html background color list = AliceBlue, Cyan, Gold, Lavender, LightGreen, PeachPuff, Wheat
html name color list = Blue, DarkCyan, DarkGoldenRod, Purple, DarkGreen, Orange, Sienna

# The background color of the thread in replies

thread background = HoneyDew


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
    """Generates a default configuration if one is not passed in"""

    f = open(filename, "w")
    f.write(DEFAULT_CONFIGURATION)
    f.close()
    return


def _get_contacts(configuration: configparser.ConfigParser) -> dict:
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
    """ Run the imessagedb command line"""

    out = sys.stdout

    logging.basicConfig(level=logging.INFO, format='%(asctime)s <%(name)s> %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger('main')
    logger.debug("Processing parameters")

    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--name", help="Person to get conversations about")

    type_mutex_group = argument_parser.add_mutually_exclusive_group()
    type_mutex_group.add_argument('--handle', help="A list of handles to search against", nargs='*')
    type_mutex_group.add_argument('--chat', help="A chat to print")

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
    argument_parser.add_argument('--start_time', '--start-time',
                                 help="The start date/time of the messages")
    argument_parser.add_argument('--end_time', '--end-time',
                                 help="The end date/time of the messages")
    argument_parser.add_argument('--split_output', '--split-output',
                                 help="Split the html output into files with this many messages per file")
    argument_parser.add_argument('--get_handles', '--get-handles',
                                 help="Display the list of handles in the database and exit", action="store_true")
    argument_parser.add_argument('--get_chats', '--get-chats',
                                 help="Display the list of chats in the database and exit", action="store_true")
    argument_parser.add_argument('--version', help="Prints the version number", action="store_true")

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
    if args.split_output:
        config.set(DISPLAY, 'split output', args.split_output)

    start_date = None
    end_date = None
    if args.start_time:
        try:
            start_date = dateutil.parser.parse(args.start_time)
        except ValueError as exp:
            argument_parser.print_help(sys.stderr)
            print(f"\n **Start time not correct: {exp}", file=sys.stderr)
            exit(1)
        config.set(CONTROL, 'start time', str(start_date))
    if args.end_time:
        try:
            end_date = dateutil.parser.parse(args.end_time)
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

    person = None
    numbers = None

    if not generic_database_request:
        if args.chat:
            person = f"chat_{args.chat}"
            if args.name:
                person = args.name
        else:
            if args.handle:
                numbers = args.handle
                if args.name:
                    person = args.name
                else:
                    person = ', '.join(numbers)
            elif args.name:
                person = args.name
                contacts = _get_contacts(config)
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

        copy_directory = config[CONTROL].get('copy directory', fallback=os.environ['HOME'])
        if copy_directory == "HOME":
            copy_directory = os.environ['HOME']
        attachment_directory = f"{copy_directory}/{safe_filename(person)}_attachments"
        config[CONTROL]['attachment directory'] = attachment_directory

        try:
            os.mkdir(attachment_directory)
        except FileExistsError:
            pass

    # Connect to the database

    database = DB(args.database, config=config)

    if args.get_handles:
        print(f"Available handles in the database:\n{database.handles.get_handles()}")
        sys.exit(0)

    if args.get_chats:
        print(f"Available chats in the database:\n{database.chats.get_chats()}")
        sys.exit(0)

    if args.chat:
        chat_id = args.chat
        title = args.chat
        if args.chat in database.chats.chat_names:
            chats = database.chats.chat_names[args.chat]
            if len(chats) != 1:
                error_string = f"You have {len(chats)} chats named {args.chat}, " \
                               f"but this program can only handle the case where there is one. " \
                               f"Rename your group and try again."
                logger.error(error_string)
                exit(1)
            chat_id = chats[0].rowid
            title = args.chat
        elif int(args.chat) in database.chats.chat_list:
            chat_id = int(args.chat)
            if database.chats.chat_list[chat_id].chat_name:
                title = database.chats.chat_list[chat_id].chat_name
            elif args.name:
                title = args.name
            else:
                title = chat_id
        else:
            logger.error(f"{args.chat} not recognized as a chat. Run 'imessagedb --get_chats' to get the list of chats")
            argument_parser.print_help()
            exit(1)

        message_list = database.Messages('chat', title, chat_id=chat_id)
    else:

        message_list = database.Messages('person', person, numbers=numbers)

    me = config.get('DISPLAY', 'me', fallback='Me')

    filename = os.path.join(copy_directory, safe_filename(person))
    output_type = config[CONTROL].get('output type', fallback='html')
    if output_type == 'text':
        database.TextOutput(me, message_list, output_file=out).print()
    else:
        database.HTMLOutput(me, message_list, output_file=filename)

    database.disconnect()


if __name__ == '__main__':
    run()
