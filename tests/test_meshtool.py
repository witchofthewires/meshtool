import re
import pytest
import sqlite3

from meshtool.__main__ import get_interface, get_channels, __version__ as meshtool_version
from meshtool.db import read_table, add_message_entry

from conftest import test_db

VERSTR_REGEX = r"^__version__ = ['\"]([^'\"]*)['\"]"

def test_always_pass():
    assert True

@pytest.mark.radio
@pytest.mark.slow
def test_radio_attached(radio):
    # fails when radio is not connected to serial port
    assert radio.devPath is not None

# https://stackoverflow.com/questions/458550/standard-way-to-embed-version-into-python-package
def test_get_version():
    with open("src\\meshtool\\_version.py") as fp:
        verstr_line = fp.read()
        res = re.search(VERSTR_REGEX, verstr_line, re.M)
        file_version = 'not_found' if not res else res.group(1)
        assert file_version == meshtool_version
'''
def test_create_db(test_db):
    with sqlite3.connect(test_db) as db_conn:
        assert db_conn is not None
        assert type(db_conn) == sqlite3.Connection
'''
def test_messages_table_read_update(test_db, sample_message):

    with sqlite3.connect(test_db) as db_conn:

        # read empty
        res = read_table(db_conn, 'messages')
        assert res == []

        # write message to table, then read back
        add_message_entry(test_db, sample_message)
        db_msg = read_table(db_conn, 'messages')[0]

        # TODO package this logic as function in db.py
        file_msg_key_fields = sample_message['fromId'], sample_message['toId'], sample_message['id'], sample_message['rxSnr'], sample_message['hopLimit'], sample_message['rxRssi'], sample_message['hopStart'], sample_message['relayNode'], sample_message['decoded']['payload']
        file_msg_key_fields_str_only = tuple([str(f) for f in file_msg_key_fields])
        assert db_msg == file_msg_key_fields_str_only

@pytest.mark.radio
@pytest.mark.slow
def test_get_channels_default_channel(radio):
    channels = get_channels(radio)
    assert channels[0].settings.psk == b'\x01'
    assert channels[0].settings.name == ''