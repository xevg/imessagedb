# imessagedb

Reads and displays the Apple iMessage database

## Installation

```bash
$ pip install imessagedb
```

## Usage

`imessagedb` can be used as a library for accessing and parsing the iMessasge chat database
stored at ~/Library/Messages/chat.db, or it can be used on the command line to display the contents.

### How it works

The command line version wraps the functions provided and outputs data based on the 
configuration available in the configuration file, as well as command line arguments.

The way that iMessage identifies conversation particpants is by a `handle`, which can be their
phone number or email address. To make it easier, you can map handles in the configuration file.

You can also specify the type of output (text or html) and the time frame of the messages. At 
this point `imesssagedb` will pull all messages from that person, regardless of the chat that it
is part of. 

If you specify html output, `imessagedb` will copy your attachments so that they are accessible
to the web browser. In addition, it will convert certain types of attachments so that they 
can be viewed in the browser. For instance, it will convert HEIC files to PNG so that they 
browser can display it, and will convert various type of movie files to mp4 and various audio
files to mp3. If you have many attachments, this can take a long time and take a lot of space. 

### Example Output

This is what the default html version looks like. Note that I am hovering over one of the
links to show the image.

![](JulioHtml.png)

This is the same conversation rendered in text.

![](JulioText.png)

### Command Line

```python
imessagedb [-h] [--handle [HANDLE ...] | --name NAME] [-c CONFIGFILE]
               [-o OUTPUT_DIRECTORY] [--database DATABASE] [-m ME]
               [-t {text,html}] [-i] [-f | --no_copy] [--no_attachments] [-v]
               [--start_time START_TIME] [--end_time END_TIME]
optional arguments:
  -h, --help            show this help message and exit
  --handle [HANDLE ...]
                        A list of handles to search against
  --name NAME           Person to get conversations about
  -c CONFIGFILE, --configfile CONFIGFILE
                        Location of the configuration file
  -o OUTPUT_DIRECTORY, --output_directory OUTPUT_DIRECTORY
                        The output directory where the output and attachments
                        go
  --database DATABASE   The database file to open
  -m ME, --me ME        The name to use to refer to you
  -t {text,html}, --output_type {text,html}
                        The type of output
  -i, --inline          Show the attachments inline
  -f, --force           Force a copy of the attachments
  --no_copy             Don't copy the attachments
  --no_attachments      Don't process attachments at all
  -v, --verbose         Turn on additional output
  --start_time START_TIME
                        The start time of the messages
  --end_time END_TIME   The end time of the messages
  --split_output SPLIT_OUTPUT
                        Split the html output into files with this many messages per file
  --version             Show the version number and exit
  --get_handles         Display the list of handles in the database and exit
  --get_chats           Display the list of chats in the database and exit
```

#### Command line options

**-h** prints a help message                                                                        |

**--handle [HANDLE ...]**  A list of handles to search against. 
For instance, '*--handle +12016781234 john@smith.com*'. 

**--name NAME** A person to search for. The mapping of person to handle is in the configuration 
file (see below) 

*** Note that you can only have one of --handle or --name, not both ***

**-c CONFIGFILE, --configfile CONFIGFILE** The location of the configuration file. If the 
file does not exist, a default configuration file will be created there. If this option is 
not provided, the default location is `~/.conf/iMessageDB.ini`.

**-o OUTPUT_DIRECTORY, --output_directory OUTPUT_DIRECTORY** The output directory where the 
output and attachments go. If this option is not provided, the default location is your
home directory. The files will be `~/NAME.html` and attachments will be in 
`~/NAME_Attachments`.

**--database DATABASE**  The database file to open. If this option is not provided it will
default to `~/Library/Messages/chat.db`, which is where Apple puts it.

**-m ME, --me ME** The name to use to refer to you in the output. If this option is not 
provided it will default to `Me`.

**-t {text,html}, --output_type {text,html}** The type of output, either *text* or *html*. 
If this option is not provided it will default to `html`.

**--start_time START_TIME** <br>
**--end_time END_TIME** By default, the program will process all messages. If you want
to restrict that to particular timeframe, you can specify the `--start-time` and/or `--end_time`
options

**--split_output SPLIT_OUTPUT** Split the html output into files with this many messages 
per file

**-i, --inline**   Show the attachments inline. By default, the attachments will show as links
that you can hover over and it will pop up the attachment. With this option, it will put them
inline, which will make your output much busier and take a lot more memory in your browser.

**-f, --force**  Force a copy of the attachments. By default, if the attachment already exists
in the destination directory, it will not re-copy the file, but this will force it to re-copy it.

**--no_copy**             Don't copy the attachments. This will make them inaccessible for 
viewing

**--no_attachments**      Do not show the attachments at all

**-v, --verbose**         Turn on additional output

**--version**  Shows the version number and exits

**--get_handles** Display the list of handles in the database and exit

**--get_chats** Display the list of chats in the database and exit
### Configuration File

The configuration file is in configparser format. Here is the template that is created
by default:

```python
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

output_type = html

# Number of messages in each html file. If this is 0 or not specified, it will be one large file.

output split = 1000

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

```


### Library Usage

```python
import imessagedb
database = imessagedb.DB()
```

- TODO - More usage here
## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`imessagedb` was created by Xev Gittler. It is licensed under the terms of the MIT license.

## Documentation

Full documentation available at https://imessagedb.readthedocs.io/en/latest/
