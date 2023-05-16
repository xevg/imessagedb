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
        self._handle_list = {}
        self._numbers = {}

        self._get_handles()
        return

    def _get_handles(self):
        self._database.connection.execute('select rowid, id, service from handle')
        rows = self._database.connection.fetchall()
        for row in rows:
            rowid = row[0]
            number = row[1]
            service = row[2]
            new_handle = Handle(self._database, rowid, number, service)
            self._handle_list[new_handle.rowid] = new_handle
            if new_handle.number in self._numbers:
                self._numbers[new_handle.number].append(new_handle)
            else:
                self._numbers[new_handle.number] = [new_handle]

    @property
    def handles(self) -> dict:
        """ Return the list of handles """
        return self._handle_list

    @property
    def numbers(self) -> dict:
        """ Return the list of handles indexed by the number """
        return self._numbers

    def __iter__(self):
        return self._handle_list

    def __len__(self) -> int:
        return len(self._handle_list)

    def __repr__(self) -> str:
        handle_array = []
        for i in sorted(self._handle_list.keys()):
            handle_array.append(self._handle_list[i])
        return '\n'.join(map(str, handle_array))
