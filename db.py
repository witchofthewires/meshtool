import sqlite3
import logging 

import utils

db_name = "meshtool.db"

#global logger
log_level = logging.INFO
logger = utils.logging_setup(__name__, log_level=log_level)
utils.logger_initialize_msg(logger, __name__, logging.DEBUG)

def create_meshdb(db_name):
    conn = sqlite3.connect(db_name)
    if not table_exists(conn, 'nodes'): init_meshdb(conn)
    return conn

def table_exists(db_conn, table_name):
    try:
        query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
        table_list = db_conn.cursor().execute(query).fetchall()
        return (len(table_list) != 0)
    except sqlite3.OperationalError as e:
        logger.error(f"sqlite3.OperationalError -  {e}")
        logger.error("table_exists did not execute properly; returning False")

# TODO more precise datatypes
def init_meshdb(db_conn):
    query = 'CREATE TABLE nodes(num_id VARCHAR(255), ' \
            'user VARCHAR(255), ' \
            'id VARCHAR(9) PRIMARY KEY, ' \
            'aka VARCHAR(4), ' \
            'hardware VARCHAR(255), ' \
            'pubkey VARCHAR(255), ' \
            'role VARCHAR(255), ' \
            'latitude VARCHAR(255), ' \
            'longitude VARCHAR(255), ' \
            'altitude VARCHAR(255), ' \
            'battery VARCHAR(255), ' \
            'channel_util VARCHAR(255), ' \
            'tx_air_util VARCHAR(255), ' \
            'snr VARCHAR(255), ' \
            'hops VARCHAR(255), ' \
            'channel VARCHAR(255), ' \
            'last_heard VARCHAR(255), ' \
            'since VARCHAR(255))'
    db_conn.cursor().execute(query)

# TODO better update query
def add_node_entry(db_conn, node):
    insert_query = 'INSERT INTO nodes VALUES %r;' % (tuple(node),)
    update_query = f'UPDATE nodes SET last_heard = "{node[-2]}";'
    with db_conn:
        try:
            db_conn.cursor().execute(insert_query)
        except sqlite3.IntegrityError:
            logger.debug(f"db entry for node {node[2]} already exists, updating")
            db_conn.cursor().execute(update_query)
            