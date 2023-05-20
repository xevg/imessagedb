from imessagedb.chat import Chat


class Chats:
    """ All Chats in the database """

    def __init__(self, database) -> None:
        """
            Parameters
            ----------
            database : imessagedb.DB
                An instance of a connected database"""

        self._database = database
        self._chat_list = {}  # Chat list by rowid
        self._chat_identifiers = {}  # Chat list by identifier
        self._chat_names = {}  # Chat list by name

        self._get_chats_from_database()
        return

    def __repr__(self) -> str:
        string_array = []
        for i in sorted(self.chat_list):
            string_array.append(str(self.chat_list[i]))
        return '\n'.join(string_array)

    def __len__(self) -> int:
        return len(self._chat_list)

    def _get_chats_from_database(self) -> None:
        self._database.connection.execute('select rowid, chat_identifier, display_name from chat')
        rows = self._database.connection.fetchall()
        for row in rows:
            rowid = row[0]
            chat_identifier = row[1]
            display_name = row[2]
            new_chat = Chat(self._database, rowid, chat_identifier, display_name)
            self.chat_list[new_chat.rowid] = new_chat

            # Add the chat to the chat_identifiers
            if new_chat.chat_identifier in self.chat_identifiers:
                self._chat_identifiers[new_chat.chat_identifier].append(new_chat)
            else:
                self._chat_identifiers[new_chat.chat_identifier] = [new_chat]

            # Add the chat to the chat_names
            if new_chat.chat_name != "":
                if new_chat.chat_name in self._chat_names:
                    self._chat_names[new_chat.chat_name].append(new_chat)
                else:
                    self._chat_names[new_chat.chat_name] = [new_chat]

        # Add the last chat date to all the chats
        for i in self.chat_list.values():
            select_string = "select " \
                    "datetime(max(message_date)/1000000000 + strftime('%s', '2001-01-01'),'unixepoch','localtime') " \
                    f"from chat_message_join cmj where chat_id = {i.rowid}"

            self._database.connection.execute(select_string)
            rows = self._database.connection.fetchall()
            i.last_message_date = rows[0][0]

        # Add the participants for all the chats
        self._database.connection.execute('select chat_id, handle_id from chat_handle_join')
        rows = self._database.connection.fetchall()
        for row in rows:
            chat_id = row[0]
            handle_id = row[1]

            self.chat_list[row[0]].add_participant(row[1])

        return

    def get_chats(self) -> str:
        """ Return a string with the list of chats in the database"""
        return_array = []
        for chat_id in sorted(self._chat_list):
            chat = self._chat_list[chat_id]
            chat_name = ""
            if chat.chat_name and chat.chat_name != '':
                chat_name = f"{chat.rowid} ({chat.chat_name}):"
            else:
                chat_name = f"{chat.rowid}:"
            chat_string = f"{chat_name} Participants: {chat.participants}, Last Message Sent: {chat.last_message_date}"
            return_array.append(chat_string)
        return '\n'.join(return_array)

    @property
    def chat_list(self) -> dict:
        """ Return the list of chats by rowid in a dict"""
        return self._chat_list

    @property
    def chat_names(self) -> dict:
        """ Return the list of chats by rowid in a dict"""
        return self._chat_names

    @property
    def chat_identifiers(self) -> dict:
        """ Return the list of chats by chat identifier in a dict"""
        return self._chat_identifiers

    def __getitem__(self, item) -> Chat:
        if item in self._chat_names:
            return self._chat_names[item]

        if item in self._chat_list:
            return self._chat_list[item]

        if item in self._chat_identifiers:
            return self._chat_identifiers[item]

        raise KeyError
