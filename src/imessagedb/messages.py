import subprocess
import os
from alive_progress import alive_bar
from imessagedb.message import Message

# The location of the translator binary is the same as this file is located.


class Messages:
    """ All messages in a conversation or conversations with a particular person """
    def __init__(self, database, person: str, numbers: list) -> None:
        """
                Parameters
                ----------
                database : imessagedb.DB
                    An instance of a connected database

                person : str
                    The name of the person in the conversation

                numbers: list
                    A list of numbers associated with the person, as represented in the handle data table

                """
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
                        " message.attributedBody, message.message_summary_info, message.text, " \
                        "reply_to_guid, thread_originator_guid, thread_originator_part, cmj.chat_id  " \
                        "from message, chat_message_join cmj " \
                        f"where message.rowid = cmj.message_id and {where_clause} " \
                        "order by message.date asc"
        row_count_string = f"select count (*) from message where {where_clause}"

        self._database.connection.execute(row_count_string)
        (row_count_total) = self._database.connection.fetchone()
        row_count_total = row_count_total[0]

        self._database.connection.execute(select_string)

        # At some point Apple switched from using the text field to also using the attributed string field.
        #  This field is not easily readable, so there is an Objective-C program that does the translation.
        #  This will be called for each message that has that field.
        translate = subprocess.Popen([translator_command], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, text=True)

        i = self._database.connection.fetchone()

        with alive_bar(row_count_total, title="Getting Messages", stats="({rate}, eta: {eta})") as bar:
            message_count = 0
            while i:
                (rowid, guid, date, is_from_me, handle_id, attributed_body, message_summary_info, text,
                 reply_to_guid, thread_originator_guid, thread_originator_part, chat_id) = i
                message_count = message_count + 1

                attachment_list = None
                if rowid in self._database.attachment_list.message_join:
                    attachment_list = self._database.attachment_list.message_join[rowid]

                skipped = True

                new_message = Message(self._database, rowid, guid, date, is_from_me, handle_id, attributed_body,
                                      message_summary_info, text, reply_to_guid, thread_originator_guid,
                                      thread_originator_part, chat_id, attachment_list)
                self._guids[guid] = new_message
                self._message_list[rowid] = new_message

                # Manage the thread
                if thread_originator_guid:
                    self._guids[thread_originator_guid].thread[rowid] = new_message

                bar(skipped=skipped)
                i = self._database.connection.fetchone()

        self._sorted_message_list = sorted(self._message_list.values(), key=lambda x: x.date)

    @property
    def message_list(self) -> list:
        """ Returns a list of messages sorted by the date of the message"""
        return self._sorted_message_list

    @property
    def guids(self) -> dict:
        return self._guids

    def __iter__(self):
        return self._sorted_message_list.__iter__()

    def __len__(self) -> int:
        return len(self._sorted_message_list)
