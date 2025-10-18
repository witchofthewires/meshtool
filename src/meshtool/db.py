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
    if not table_exists(conn, 'nodes'): init_meshdb(conn, can_drop=True)
    if not table_exists(conn, 'messages'): init_meshdb(conn, can_drop=True)
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
def init_meshdb(db_conn, can_drop=False):

    if can_drop:
        query = 'DROP TABLE nodes; DROP TABLE messages'
        db_conn.cursor().execute(query)

    # nodes table
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
    try:
        db_conn.cursor().execute(query)
    except sqlite3.OperationalError:
        logger.info(f"Cannot create table nodes, as it already exists, and can_drop={can_drop}")

    # messages table
    query = 'CREATE TABLE messages(from_id VARCHAR(255), ' \
            'to_id VARCHAR(255), ' \
            'id VARCHAR(255) PRIMARY KEY, ' \
            'rx_snr VARCHAR(255), ' \
            'hop_limit VARCHAR(255), ' \
            'rx_rssi VARCHAR(255), ' \
            'hop_start VARCHAR(255), ' \
            'relay_node VARCHAR(255), ' \
            'payload VARCHAR(255))'
    try:
        db_conn.cursor().execute(query)
    except sqlite3.OperationalError:
        logger.info(f"Cannot create table messages, as it already exists, and can_drop={can_drop}")
    
# TODO better update query
def add_node_entry(db_conn, node):

    ''' meshtastic/mesh_interface.py lines 237-254
                    name_map = {
                    "user.longName": "User",
                    "user.id": "ID",
                    "user.shortName": "AKA",
                    "user.hwModel": "Hardware",
                    "user.publicKey": "Pubkey",
                    "user.role": "Role",
                    "position.latitude": "Latitude",
                    "position.longitude": "Longitude",
                    "position.altitude": "Altitude",
                    "deviceMetrics.batteryLevel": "Battery",
                    "deviceMetrics.channelUtilization": "Channel util.",
                    "deviceMetrics.airUtilTx": "Tx air util.",
                    "snr": "SNR",
                    "hopsAway": "Hops",
                    "channel": "Channel",
                    "lastHeard": "LastHeard",
                    "since": "Since",
    '''

    insert_query = 'INSERT INTO nodes VALUES %r;' % (tuple(node),)
    update_query = f'UPDATE nodes SET last_heard = "{node[-2]}";'
    with db_conn:
        try:
            db_conn.cursor().execute(insert_query)
        except sqlite3.IntegrityError:
            logger.debug(f"db entry for node {node[2]} already exists, updating")
            db_conn.cursor().execute(update_query)

def add_message_entry(db_name, packet):

    db_conn = sqlite3.connect(db_name)

    # TODO figure out why this is needed
    desired_fields = ['fromId', 'toId', 'id', 'rxSnr', 'hopLimit', 'rxRssi', 'hopStart', 'relayNode', 'decoded']
    for field in desired_fields:
        if field not in packet: packet[field] = 'UNK'

    insert_query = 'INSERT INTO messages VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'
    try:
        insert_params = packet['fromId'], packet['toId'], packet['id'], packet['rxSnr'], packet['hopLimit'], packet['rxRssi'], packet['hopStart'], packet['relayNode'], packet['decoded']['payload']
    except KeyError as e:
        logger.error(f"Failed to parse message field: {e}")
        logger.error(f"Failed to write message to database")
        print(packet)
        return
    with db_conn:
        try:
            db_conn.cursor().execute(insert_query, insert_params)
        except sqlite3.IntegrityError:
            logger.error(f"Failed to write message to database")
            return
        except sqlite3.OperationalError as e:
            logger.error(f"Unexpected error in writing message to database")
            print(insert_query)
            print(insert_params)
            return
    logger.info(f"Logged message from {packet['fromId']} to {packet['toId']}: {packet['decoded']['payload']}")
            
            