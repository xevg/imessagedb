import os
import urllib.parse
import re
import shutil


class Attachment:
    def __init__(self, rowid, filename, mime_type, copy=False, copy_directory=None, home_directory=os.environ['HOME']):
        self._rowid = rowid
        self._filename = filename
        self._mime_type = mime_type
        self._copy = copy
        self._copy_directory = copy_directory
        self._home_directory = home_directory

        self._destination_path = None
        self._popup_type = None
        self._conversion_type = None
        self._skip = False
        self._missing = False
        self._needs_conversion = False

        # The path is set to use ~, so replace it with the home directory
        self._original_path = self._filename.replace('~', self._home_directory)
        if not os.path.exists(self._original_path):
            self._missing = True
            return

        if self._copy_directory is None or not os.path.exists(self._copy_directory):
            self._copy = False

        if self._copy:
            parts = self._original_path.split('/')
            last = parts.pop()
            penultimate = parts.pop()
            self._destination_filename = f'{penultimate}-{last}'

        self.process_mime_type()  # We may need to do a conversion and therefore change the filename
        if copy:
            self._destination_path = f'{self._copy_directory}/{self._destination_filename}'
        else:
            self._destination_path = self._original_path

        return

    @property
    def rowid(self):
        return self._rowid

    @property
    def filename(self):
        return self._filename

    @property
    def mime_type(self):
        return self._mime_type

    @property
    def copy(self):
        return self._copy

    @property
    def destination_path(self):
        return self._destination_path

    @property
    def popup_type(self):
        return self._popup_type

    @property
    def conversion_type(self):
        return self._conversion_type

    @property
    def skip(self):
        return self._skip

    @property
    def missing(self):
        return self._missing

    @property
    def original_path(self):
        return self._original_path

    @property
    def destination_filename(self):
        return self._destination_filename

    @property
    def html_path(self):
        return urllib.parse.quote(self.destination_path)

    @property
    def link_path(self):
        return f"file://{urllib.parse.quote(self.destination_path)}"

    def process_mime_type(self):
        if self._mime_type is None:
            # The only type of file that doesn't have a mime type that I am currently interested in are audio files
            search_name = re.search(".caf$", self._filename)
            if search_name:
                self._popup_type = "Audio"
                self._conversion_type = "AV"
                if self.copy:
                    self._destination_filename = f'{self._destination_filename}.mp3'
            else:
                self._skip = True  # We don't care about this attachment

        elif self._mime_type[0:5] == "image":
            self._popup_type = "Picture"
            if self.mime_type == 'image/heic':
                self._conversion_type = "HEIC"
                if self._copy:
                    self._destination_filename = f'{self._destination_filename}.png'

        # Process audio
        elif self._mime_type[0:5] == "audio":
            self._popup_type = "Audio"
            self._conversion_type = "Audio"
            if self._copy:
                self._destination_filename = f'{self._destination_filename}.mp3'

        # Process Video
        elif self._mime_type[0:5] == "video":
            self._popup_type = "Video"
            if self.mime_type != "video/mp4":
                self._conversion_type = "Video"
                if self.copy:
                    self._destination_filename = f'{self._destination_filename}.mp4'

    def copy_file(self):
        print(f"Copying {self._destination_filename}")
        try:
            shutil.copyfile(self._original_path, self._destination_path)
            return self._destination_path
        except:
            return None


