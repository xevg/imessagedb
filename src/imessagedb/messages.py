from imessagedb.utils import *
from alive_progress import alive_bar
from imessagedb.message import Message


class Messages:
    """ All messages in a conversation or conversations with a particular person """

    def __init__(self, database, query_type: str, title: str, numbers: list = None, chat_id: str = None) -> None:
        """
                Parameters
                ----------
                database : imessagedb.DB
                    An instance of a connected database

                query_type : str
                    The type of messages, either 'person' or 'chat'

                title : str
                    The name of the conversation

                numbers : list
                    A list of numbers associated with the person, as represented in the handle data table

                chat_id : str
                    The id of the chat
                """

        self._database = database
        self._query_type = query_type
        self._numbers = numbers
        self._chat_id = chat_id
        self._title = title
        self._guids = {}
        self._message_list = {}

        time_rules = []
        time_where_clause = ""
        start_time = self._database.control.get('start time', fallback=None)
        end_time = self._database.control.get('end time', fallback=None)
        if start_time:
            database_start_date = convert_to_database_date(start_time)
            time_rules.append(f"message.date >= {database_start_date}")
        if end_time:
            database_end_date = convert_to_database_date(end_time)
            time_rules.append(f"message.date <= {database_end_date}")
        if len(time_rules) > 0:
            time_where_clause = f" and {' AND '.join(time_rules)}"

        if self._query_type == "person":
            numbers_string = "','".join(self._numbers)
            where_clause = "rowid in (" \
                           " select message_id from chat_message_join where chat_id in (" \
                           "  select chat_id from chat_handle_join where handle_id in (" \
                           f"   select rowid from handle where id in ('{numbers_string}')" \
                           "  )" \
                           " )" \
                           f") {time_where_clause}"
            select_string = "select message.rowid, guid, " \
                            "datetime(message.date/1000000000 + " \
                            "strftime('%s', '2001-01-01'),'unixepoch','localtime'), " \
                            "message.is_from_me, message.handle_id, " \
                            " message.attributedBody, message.message_summary_info, message.text, " \
                            "reply_to_guid, thread_originator_guid, thread_originator_part, cmj.chat_id  " \
                            "from message, chat_message_join cmj " \
                            f"where message.rowid = cmj.message_id and {where_clause} " \
                            "order by message.date asc"

        elif self._query_type == "chat":
            where_clause = f"rowid in (select message_id from chat_message_join where chat_id = {self._chat_id}) " \
                           f" {time_where_clause}"
            select_string = "select message.rowid, guid, " \
                            "datetime(message.date/1000000000 + " \
                            "strftime('%s', '2001-01-01'),'unixepoch','localtime'), " \
                            "message.is_from_me, message.handle_id, " \
                            " message.attributedBody, message.message_summary_info, message.text, " \
                            "reply_to_guid, thread_originator_guid, thread_originator_part, cmj.chat_id  " \
                            "from message, chat_message_join cmj " \
                            f"where message.rowid = cmj.message_id and {where_clause} " \
                            "order by message.date asc"

        else:
            raise KeyError

        row_count_string = f"select count (*) from message where {where_clause}"

        self._database.connection.execute(row_count_string)
        (row_count_total) = self._database.connection.fetchone()
        row_count_total = row_count_total[0]

        self._database.connection.execute(select_string)

        i = self._database.connection.fetchone()
        skip_attachment = self._database.control.getboolean('skip attachments', fallback=False)

        with alive_bar(row_count_total, title="Getting Messages", stats="({rate}, eta: {eta})") as bar:
            message_count = 0
            while i:
                (rowid, guid, date, is_from_me, handle_id, attributed_body, message_summary_info, text,
                 reply_to_guid, thread_originator_guid, thread_originator_part, chat_id) = i
                message_count = message_count + 1

                attachment_list = None
                if not skip_attachment:
                    if rowid in self._database.attachment_list.message_join:
                        attachment_list = self._database.attachment_list.message_join[rowid]

                new_message = Message(self._database, rowid, guid, date, is_from_me, handle_id, attributed_body,
                                      message_summary_info, text, reply_to_guid, thread_originator_guid,
                                      thread_originator_part, chat_id, attachment_list)
                self._guids[guid] = new_message
                self._message_list[rowid] = new_message

                # Manage the thread
                if thread_originator_guid and thread_originator_guid in self._guids:
                    self._guids[thread_originator_guid].thread[rowid] = new_message

                bar()
                i = self._database.connection.fetchone()

        self._sorted_message_list = sorted(self._message_list.values(), key=lambda x: x.date)

    @property
    def message_list(self) -> list:
        """ Returns a list of messages sorted by the date of the message"""
        return self._sorted_message_list

    def stats(self) -> list:
        """ Returns a list of stats about the message list suitable for importing into a spreadsheet.

         The fields returned are:
            name: The name of the person sending the message
            date: The date of the message
            character_count: The number of characters in the message
            word_count: The number of words in the message
            text: The text of the message
        """

        result = []

        for i in self._sorted_message_list:
            if i.text is not None:
                # Take out the carriage returns so this can be parsed by a spreadsheet
                text = i.text.replace('\n', ' ')
                text_len = len(i.text)
                word_count = len(i.text.split(' '))
            else:
                text = ""
                text_len = 0
                word_count = 0
            date = i.date
            stats = {'name': i.name, 'date': date, 'character_count': text_len, 'word_count': word_count, 'text': text}
            result.append(stats)
        return result

    def print_stats(self) -> str:
        """ Returns a string of stats about the message list suitable for importing into a spreadsheet """

        result = ["Name\tDate\tCharacter Count\tWord Count\tText"]
        for i in self.stats():
            result.append(f"{i['name']}\t{i['date']}\t{i['character_count']}\t{i['word_count']}\t{i['text']}")
        return '\n'.join(result)

    @property
    def guids(self) -> dict:
        return self._guids

    @property
    def title(self) -> str:
        return self._title

    def __iter__(self):
        return self._sorted_message_list.__iter__()

    def __len__(self) -> int:
        return len(self._sorted_message_list)
