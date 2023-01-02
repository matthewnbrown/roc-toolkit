import os
from pathlib import Path
from bs4 import BeautifulSoup


def _get_dir():
    path = Path(__file__)
    return str(path.parent.parent.parent.absolute())


def _check_tfile_exists(path):
    if not os.path.exists(path):
        raise Exception(f'File does not exist at {path}')


def get_text_from_file(path):
    filepath = _get_dir() + path
    _check_tfile_exists(filepath)
    with open(filepath) as f:
        text = f.read()
    return text


def getsoup(path):
    text = get_text_from_file(path)
    soup = BeautifulSoup(text, 'lxml')
    return soup
