import os
from pathlib import Path
from bs4 import BeautifulSoup


def _get_dir():
    path = Path(__file__)
    return str(path.parent.parent.parent.absolute())


def _check_tfile_exists(path):
    if not os.path.exists(path):
        raise Exception(f'File does not exist at {path}')


def getsoup(path):
    filepath = _get_dir() + path
    _check_tfile_exists(filepath)

    with open(filepath) as f:
        text = f.read()
        soup = BeautifulSoup(text, 'lxml')
    return soup


