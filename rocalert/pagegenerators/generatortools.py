import datetime as dt


def timestamp_to_datetime(timestamp: int) -> dt.datetime:
    return dt.datetime.fromtimestamp(timestamp)


def rocnum_to_int(num_as_str: str):
    value = num_as_str.strip().split(' ')[0].strip()
    value = value.replace(',', '')
    return int(value)


def int_to_rocnum(num: int):
    return f'{num:,}'
