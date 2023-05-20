from imessagedb.handle import Handle


class Handles:
    """ All handles in the database """

    def __init__(self, database) -> None:
        """
            Parameters
            ----------
            database : imessagedb.DB
                An instance of a connected database
        """
        self._database = database
        self._handle_list = {}  # Handles by rowid
        self._numbers = {}  # Handles by phone number / email
        self._names = {}  # Handles by name (from contact list)
        self._contacts_by_name = {}
        self._contacts_by_number = {}

        # Process the contacts first
        if self._database.config.has_section('CONTACTS'):
            for (key, value) in self._database.config.items('CONTACTS'):
                # Capitalize the first letter of every word, since configparser loses case
                key = key.title()
                value = value.replace('\n', '')
                values = value.split(',')
                self._contacts_by_name[key] = values
                for item in values:
                    self._contacts_by_number[item] = key

        self._get_handles_from_database()
        return

    def _get_handles_from_database(self):

        self._database.connection.execute('select rowid, id, service from handle')
        rows = self._database.connection.fetchall()
        for row in rows:
            rowid = row[0]
            number = row[1]
            service = row[2]
            if number in self._contacts_by_number:
                name = self._contacts_by_number[number]
            else:
                name = number
            new_handle = Handle(self._database, rowid, name, number, service)

            # Add the handle to the rowid dictionary
            self._handle_list[new_handle.rowid] = new_handle

            # Add the handle to the numbers dictionary
            if new_handle.number in self._numbers:
                self._numbers[new_handle.number].append(new_handle)
            else:
                self._numbers[new_handle.number] = [new_handle]

            # Add the handle to the names dictionary
            if new_handle.number in self._contacts_by_number:
                name = self._contacts_by_number[new_handle.number]
                if name in self._names:
                    self.names[name].append(new_handle)
                else:
                    self._names[name] = [new_handle]

    def get_handles(self) -> str:
        """ Return a string with the list of handles"""

        number_list = list(self._numbers.keys())
        return_string = '\n'.join(number_list)
        return return_string

    @property
    def handles(self) -> dict:
        """ Return the list of handles """
        return self._handle_list

    @property
    def numbers(self) -> dict:
        """ Return the list of handles indexed by the number """
        return self._numbers

    @property
    def names(self) -> dict:
        """ Return the list of handles indexed by the number """
        return self._names

    def name_for_number(self, number: str) -> str:
        if number in self._contacts_by_number:
            return self._contacts_by_number[number]

        return None

    def __iter__(self):
        return self._handle_list

    def __len__(self) -> int:
        return len(self._handle_list)

    def __repr__(self) -> str:
        handle_array = []
        for i in sorted(self._handle_list.keys()):
            handle_array.append(self._handle_list[i])
        return '\n'.join(map(str, handle_array))

    def __getitem__(self, item: str) -> Handle:
        if item in self._names:
            return self._names[item]

        if item in self._numbers:
            return self._numbers[item]

        raise KeyError


