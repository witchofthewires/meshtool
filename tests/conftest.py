import os
import tempfile

from meshtool import db
from meshtool.db import create_meshdb

import pytest

with open(os.path.join(os.path.dirname(__file__), 'test_meshtool_setup.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')

@pytest.fixture
def test_db():

    db_fd, db_path = tempfile.mkstemp()

    app = create_meshdb(db_path)

    yield app

    app.close()
    os.close(db_fd)
    os.unlink(db_path)