import datetime as dt
import dataclasses


def dataclass_from_dict(klass, d):
    try:
        fieldtypes = {f.name: f.type for f in dataclasses.fields(klass)}
        return klass(**{f: dataclass_from_dict(
            fieldtypes[f], d[f]) for f in d})
    except: # noqa E722
        return d  # Not a dataclass field


def timestamp_to_datetime(timestamp: int) -> dt.datetime:
    return dt.datetime.fromtimestamp(timestamp)


def rocnum_to_int(num_as_str: str):
    value = num_as_str.strip().split(' ')[0].strip()
    value = value.replace(',', '')
    return int(value)


def int_to_rocnum(num: int):
    return f'{num:,}'
