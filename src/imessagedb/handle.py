
class Handle:
    """ Class for holding information about a Handle """

    def __init__(self, database, rowid: str, name: str, number: str, service: str) -> None:
        """
            Parameters
            ----------
            database : imessagedb.DB
                An instance of a connected database

            rowid, number, service : str
                The parameters are the fields in the database

            name : str
                A name to associate with it, from the contacts list"""

        self._database = database
        self._rowid = rowid
        self._number = number
        self._service = service
        self._name = name.title()

    def __repr__(self) -> str:
        return f'{self._rowid}: Name => {self._name}, ID => {self._number}, Service => {self._service} '

    @property
    def rowid(self) -> str:
        return self._rowid

    @property
    def number(self) -> str:
        return self._number

    @property
    def service(self) -> str:
        return self._service

    @property
    def name(self) -> str:
        return self._name

