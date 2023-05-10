import subprocess
from alive_progress import alive_bar
import iMessageDB

translator_command = "/Users/xev/Dropbox/message_scripts/MessageTranslator/MessageTranslator/MessageTranslator"

verbose = True


class Messages:
    def __init__(self, database, person, numbers, attachments):
        self._database = database
        self._person = person
        self._numbers = numbers
        self._guids = {}
        self._message_list = {}

        numbers_string = "','".join(self._numbers)
        where_clause = "rowid in (" \
            " select message_id from chat_message_join where chat_id in (" \
            "  select chat_id from chat_handle_join where handle_id in (" \
            f"   select rowid from handle where id in ('{numbers_string}')" \
            "  )" \
            " )" \
            ")"
        select_string = "select message.rowid, guid, " \
                        "datetime(message.date/1000000000 + strftime('%s', '2001-01-01'),'unixepoch','localtime'), " \
                        "message.is_from_me, message.handle_id, " \
                        " hex(message.attributedBody), message.text, " \
                        "reply_to_guid, thread_originator_guid, thread_originator_part, cmj.chat_id  " \
                        "from message, chat_message_join cmj " \
                        f"where message.rowid = cmj.message_id and {where_clause} " \
                        "order by message.date asc"
        row_count_string = f"select count (*) from message where {where_clause}"

        self._database.cursor.execute(row_count_string)
        (row_count_total) = self._database.cursor.fetchone()
        row_count_total = row_count_total[0]

        self._database.cursor.execute(select_string)

        # Start the process to translate attributed strings
        # process = subprocess.Popen([translator_command], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        #                           stderr=subprocess.PIPE)

        messages = []
        i = self._database.cursor.fetchone()

        with alive_bar(row_count_total, title="Getting Messages", stats="({rate}, eta: {eta})") as bar:
            message_count = 0
            while i:
                (rowid, guid, date, is_from_me, handle_id, attributed_body, text,
                 reply_to_guid, thread_originator_guid, thread_originator_part, chat_id) = i
                message_count = message_count + 1

                attachment_list = None
                if rowid in attachments.message_join:
                    attachment_list = attachments.message_join[rowid]

                skipped = True
                if text is None:
                    # There are a lot of messages that are saved into attributed_body instead of the text field.
                    #  There isn't a good way to convert this in Python that I've found, so I have to run a
                    #  program to do it. I need to fix this.
                    if attributed_body is not None and attributed_body != '':
                        skipped = False
                        output = subprocess.run([translator_command, attributed_body], stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE)
                        text = output.stdout.decode('utf-8')

                new_message = iMessageDB.Message(rowid, guid, date, is_from_me, handle_id, attributed_body, text,
                                                 reply_to_guid, thread_originator_guid, thread_originator_part,
                                                 chat_id, attachment_list)
                self._guids[guid] = new_message
                self._message_list[rowid] = new_message

                # Manage the thread
                if thread_originator_guid:
                    self._guids[thread_originator_guid].thread[rowid] = new_message

                bar(skipped=skipped)
                i = self._database.cursor.fetchone()

        self._sorted_message_list = sorted(self._message_list.values(), key=lambda x: x.date)

    @property
    def message_list(self):
        # Return a list sorted by the date of the message
        return self._sorted_message_list

    @property
    def guids(self):
        return self._guids

    def __iter__(self):
        return self._sorted_message_list.__iter__()

    def __len__(self):
        return len(self._sorted_message_list)
