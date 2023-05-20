""" Utility functions for the class """

from datetime import datetime

mac_epoch_start = int(datetime(2001, 1, 1, 0, 0, 0).strftime('%s'))


def convert_to_database_date(date_string: str) -> float:
    date_ = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
    epoch_date = int(date_.strftime('%s'))
    diff = epoch_date - mac_epoch_start
    return diff * 1000000000


def convert_from_database_date(date_value: float) -> datetime:
    # date_ = date_value / 1000000000
    epoch_date = date_value + mac_epoch_start
    return datetime.fromtimestamp(epoch_date)


def safe_filename(filename: str) -> str:
    safe_name = filename.replace(' ', '_')
    return safe_name
