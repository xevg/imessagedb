
class Handle:
    def __init__(self, database, rowid, number, service):
        self._database = database
        self._rowid = rowid
        self._number = number
        self._service = service
        self._name = "Unknown"

    def __repr__(self):
        return f'{self._rowid}: ID => {self._number}, Service => {self._service}, Name => {self._name}'

    @property
    def rowid(self):
        return self._rowid

    @property
    def number(self):
        return self._number

    @property
    def service(self):
        return self._service

    @property
    def name(self):
        return self._name

