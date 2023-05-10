import imessagedb


class Handles:
    def __init__(self, database):
        self._database = database
        self._handle_list = {}
        self._numbers = {}

        self.get_handles()
        return

    def get_handles(self):
        self._database.connection.execute('select rowid, id, service from handle')
        rows = self._database.connection.fetchall()
        for row in rows:
            rowid = row[0]
            number = row[1]
            service = row[2]
            new_handle = imessagedb.Handle(self._database, rowid, number, service)
            self._handle_list[new_handle.rowid] = new_handle
            if new_handle.number in self._numbers:
                self._numbers[new_handle.number].append(new_handle)
            else:
                self._numbers[new_handle.number] = [new_handle]

    @property
    def handles(self):
        return self._handle_list

    @property
    def numbers(self):
        return self._numbers

    def __iter__(self):
        return self._handle_list

    def __len__(self):
        return len(self._handle_list)

    def __repr__(self):
        handle_array = []
        for i in sorted(self._handle_list.keys()):
            handle_array.append(self._handle_list[i])
        return '\n'.join(map(str, handle_array))
