import re
import pytest
import sqlite3

from meshtool.meshtool import get_interface, __version__ as meshtool_version

from conftest import test_db

VERSTR_REGEX = r"^__version__ = ['\"]([^'\"]*)['\"]"

def test_always_pass():
    assert True

@pytest.mark.radio
@pytest.mark.slow
def test_radio_attached(capsys):
    # fails when radio is not connected to serial port
    interface = get_interface()
    cap = capsys.readouterr()
    # TODO better way to check than reading error message directly
    # TODO cleaner pytest output
    returned_radio_not_connected_error = (cap.out == 
                                          "No Serial Meshtastic device detected, attempting TCP connection on localhost.\n")
    assert not returned_radio_not_connected_error
    assert interface is not None

# https://stackoverflow.com/questions/458550/standard-way-to-embed-version-into-python-package
def test_get_version():
    with open("src\\meshtool\\_version.py") as fp:
        verstr_line = fp.read()
        res = re.search(VERSTR_REGEX, verstr_line, re.M)
        file_version = 'not_found' if not res else res.group(1)
        assert file_version == meshtool_version

def test_create_db(test_db):
    assert test_db is not None
    assert type(test_db) == sqlite3.Connection