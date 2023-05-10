import os
import iMessageDB
from alive_progress import alive_bar


class Attachments:
    def __init__(self, database, copy=False, copy_directory=None, home_directory=os.environ['HOME']):
        self._database = database
        self._copy = copy
        self._copy_directory = copy_directory
        self._home_directory = home_directory

        self._attachment_list = {}
        self._message_join = {}

        # Get the list of all the attachments

        self._database.cursor.execute('select count(rowid)from attachment')
        (row_count_total) = self._database.cursor.fetchone()
        row_count_total = row_count_total[0]

        self._database.cursor.execute('select rowid, filename, mime_type from attachment')

        i = self._database.cursor.fetchone()
        with alive_bar(row_count_total, title="Getting Attachments", stats="({rate}, eta: {eta})") as bar:
            while i:
                rowid = i[0]
                filename = i[1]
                mime_type = i[2]
                if filename is not None:
                    self.attachment_list[rowid] = iMessageDB.Attachment(rowid, filename, mime_type,
                                                                        copy=self._copy,
                                                                        copy_directory=self._copy_directory)
                bar()
                i = self._database.cursor.fetchone()

        # Get the join of attachments and messages

        self._database.cursor.execute('select message_id, attachment_id from message_attachment_join')
        i = self._database.cursor.fetchone()
        while i:
            message_id = i[0]
            attachment_id = i[1]
            if message_id in self.message_join:
                self.message_join[message_id].append(attachment_id)
            else:
                self.message_join[message_id] = [attachment_id]
            i = self._database.cursor.fetchone()

        return

    @property
    def attachment_list(self):
        return self._attachment_list

    @property
    def message_join(self):
        return self._message_join

    def __iter__(self):
        return self.attachment_list.__iter__()

    def __len__(self):
        return len(self.attachment_list.keys())
