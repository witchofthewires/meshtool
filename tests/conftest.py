import os
import tempfile
import json

from meshtool import db
from meshtool.db import create_meshdb, add_message_entry

import pytest

@pytest.fixture
def sample_message():
    with open(os.path.join(os.path.dirname(__file__), 'sample_message.json'), 'rb') as fp:
        message_obj = json.load(fp)    
    return message_obj

@pytest.fixture
def test_db():

    db_fd, db_path = tempfile.mkstemp()
    db_conn = create_meshdb(db_path)
    db_conn.close()

    yield db_path

    os.close(db_fd)
    #os.unlink(db_path) # TODO this always errors bc file still in use