"""
provides access to the iMessage chat.db, including parsing and output

"""
from importlib.metadata import version

# read version from installed package

__version__ = version("imessagedb")

import os
import configparser
import logging
import argparse
import sys
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

# Some extra verbosity if true

verbose = True

[DISPLAY]

# Output type, either html or text

output_type = html

# Inline attachments mean that the images are in the HTML instead of loaded when hovered over

inline attachments = False

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

Ashley: +18484676050, ashleywilliams_@live.com, sparkette325@yahoo.com, +17325722108,
   williaa2@kean.edu
Abe: +16103499696
Alisha: +15082088327
Emily: +12672803303
Hermosa: +17329103453
Kanani: +17325351530
Randi: +16093394399
Rose: fhecla@gmail.com, +16109602522
Marta: +19172974204
Maxine: mlee99@optonline.net, panda9966@gmail.com, +19084725929, +17323816580
Monika: +19176678993, mnowak2@binghamton.edu, Xplsumnerx@gmail.com
Michele: +12153917169
Marissa: +14016490739
Lily: lilyyalexb@gmail.com, njlibrn@yahoo.com, +17327887245
Daniel: daniel@gittler.com, +17326460220, dsg1002@gmail.com, gittlerd@gmail.com, dgittler@berklee.edu
Kandela: +17324849684
Tiffany: Wickedblueglow@gmail.com, Tlgreenberg80@gmail.com, +17327105145
Jessica: jessica.marozine@icloud.com, jessica.marozine@gmail.com, +17326923688
Becky: rebecca@schore.org, +17329838356
Lynda: lylasmith559@yahoo.com, lylalombardi@icloud.com, +17323001586
Stefanie: stefanie.thomas2@gmail.com, thostefa@kean.edu, +17326101065
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
        _create_default_configuration(args.configfile)
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

    database = DB(args.database, config=config)
    message_list = database.Messages(person, contacts[person.lower()])

    if config[CONTROL]['output type'] == 'text':
        database.TextOutput(args.me, person, message_list, database.attachment_list, output_file=out).print()
    else:
        database.HTMLOutput(args.me, person, message_list, database.attachment_list, output_file=out)

    print("The end")
    database.disconnect()


if __name__ == '__main__':
    run()
