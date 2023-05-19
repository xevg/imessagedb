from imessagedb.attachment import Attachment
from alive_progress import alive_bar


class Attachments:
    """ All attachments """
    def __init__(self, database, copy=None, copy_directory=None) -> None:
        """
            Parameters
            ----------
            database : imessagedb.DB
                An instance of a connected database

            copy : bool
                Whether or not to copy attachments, default is to use the configuration parameter

            copy_directory : str
                The directory to copy attachments into
        """

        self._database = database
        if copy is None:
            self._copy = self._database.control.getboolean('copy', fallback=False)
        else:
            self._copy = copy

        if copy_directory is None:
            self._copy_directory = self._database.control.get('attachment directory', fallback="/tmp/attachments")
        else:
            self._copy_directory = copy_directory

        self._attachment_list = {}
        self._message_join = {}

        # Get the list of all the attachments, unless we are skipping them

        if self._database.control.getboolean('skip attachments', fallback=False):
            return

        self._database.connection.execute('select count(rowid)from attachment')
        (row_count_total) = self._database.connection.fetchone()
        row_count_total = row_count_total[0]

        self._database.connection.execute('select rowid, filename, mime_type from attachment')

        i = self._database.connection.fetchone()
        with alive_bar(row_count_total, title="Getting Attachments", stats="({rate}, eta: {eta})") as bar:
            while i:
                rowid = i[0]
                filename = i[1]
                mime_type = i[2]
                if filename is not None:
                    self.attachment_list[rowid] = Attachment(self._database, rowid, filename, mime_type,
                                                             copy=self._copy,
                                                             copy_directory=self._copy_directory)
                bar()
                i = self._database.connection.fetchone()

        # Get the join of attachments and messages

        self._database.connection.execute('select message_id, attachment_id from message_attachment_join')
        i = self._database.connection.fetchone()
        while i:
            message_id = i[0]
            attachment_id = i[1]
            if message_id in self.message_join:
                self.message_join[message_id].append(attachment_id)
            else:
                self.message_join[message_id] = [attachment_id]
            i = self._database.connection.fetchone()

        return

    @property
    def attachment_list(self) -> dict:
        """ Return the dictionary of all attachments """
        return self._attachment_list

    @property
    def message_join(self) -> dict:
        """ Return the mapping of messages to attachments """
        return self._message_join

    def __iter__(self):
        return self.attachment_list.__iter__()

    def __len__(self) -> int:
        return len(self.attachment_list.keys())
