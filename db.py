import sqlite3
import logging 

import utils

db_name = "meshtool.db"

#global logger
log_level = logging.INFO
logger = utils.logging_setup(__name__, log_level=log_level)
utils.logger_initialize_msg(logger, __name__, logging.DEBUG)

def create_meshdb(db_name):
    """
    Connects to the database and ensures all necessary tables are created if they don't exist.
    """
    conn = sqlite3.connect(db_name)
    _create_nodes_table_if_not_exists(conn)
    _create_messages_table_if_not_exists(conn)
    return conn

def table_exists(db_conn, table_name):
    """
    Checks if a given table exists in the database.
    """
    try:
        query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
        table_list = db_conn.cursor().execute(query).fetchall()
        return len(table_list) != 0
    except sqlite3.OperationalError as e:
        logger.error(f"sqlite3.OperationalError - {e}")
        logger.error("table_exists did not execute properly; returning False")
        return False

def _create_nodes_table_if_not_exists(db_conn):
    """
    Creates the 'nodes' table if it does not already exist.
    Using more precise datatypes for better storage and querying.
    """
    query = '''
        CREATE TABLE IF NOT EXISTS nodes(
            num_id INTEGER,
            user TEXT,
            id TEXT PRIMARY KEY,
            aka TEXT,
            hardware TEXT,
            pubkey TEXT,
            role TEXT,
            latitude REAL,
            longitude REAL,
            altitude REAL,
            battery INTEGER,
            channel_util REAL,
            tx_air_util REAL,
            snr REAL,
            hops INTEGER,
            channel INTEGER,
            last_heard REAL, -- Unix timestamp
            since REAL -- Unix timestamp
        )
    '''
    try:
        db_conn.cursor().execute(query)
        logger.debug("Nodes table ensured to exist.")
    except sqlite3.OperationalError as e:
        logger.error(f"Failed to create nodes table: {e}")

def _create_messages_table_if_not_exists(db_conn):
    """
    Creates the 'messages' table if it does not already exist.
    Using more precise datatypes.
    """
    query = '''
        CREATE TABLE IF NOT EXISTS messages(
            from_id TEXT,
            to_id TEXT,
            id TEXT PRIMARY KEY,
            rx_snr REAL,
            hop_limit INTEGER,
            rx_rssi REAL,
            hop_start INTEGER,
            relay_node TEXT,
            payload TEXT
        )
    '''
    try:
        db_conn.cursor().execute(query)
        logger.debug("Messages table ensured to exist.")
    except sqlite3.OperationalError as e:
        logger.error(f"Failed to create messages table: {e}")
    
def add_node_entry(db_conn, node_data):
    """
    Adds a new node entry or updates an existing one in the 'nodes' table.
    Uses INSERT OR REPLACE for efficiency and safety against SQL injection.
    
    Expected node_data to be a list/tuple matching the column order:
    (num_id, user, id, aka, hardware, pubkey, role, latitude, longitude,
     altitude, battery, channel_util, tx_air_util, snr, hops, channel,
     last_heard, since)
    """
    
    # Ensure node_data matches the expected number of columns (18)
    if not isinstance(node_data, (list, tuple)) or len(node_data) != 18:
        logger.error(f"Invalid node_data format for add_node_entry. Expected a list/tuple of 18 items, got: {node_data}")
        return

    # Using INSERT OR REPLACE to handle both new nodes and updates efficiently.
    # This assumes 'id' is the primary key and all other fields should be updated if the node exists.
    insert_or_replace_query = '''
        INSERT OR REPLACE INTO nodes (
            num_id, user, id, aka, hardware, pubkey, role, latitude, longitude,
            altitude, battery, channel_util, tx_air_util, snr, hops, channel,
            last_heard, since
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''

    try:
        with db_conn:
            db_conn.cursor().execute(insert_or_replace_query, node_data)
        
        # Check if a new row was inserted or an existing one updated
        # This is a bit tricky with INSERT OR REPLACE, as rowcount can be 1 for both.
        # For a simple log, just report success.
        logger.info(f"Node entry for ID '{node_data[2]}' successfully added/updated.")
    except sqlite3.Error as e:
        logger.error(f"Failed to add/update node entry '{node_data[2]}': {e}")

def add_message_entry(db_name, packet):
    """
    Adds a message entry to the 'messages' table.
    Handles varying structures of the 'decoded' field to robustly extract payload.
    """
    db_conn = sqlite3.connect(db_name)

    payload_content = None
    decoded_data = packet.get('decoded')

    # Robustly extract payload content
    if decoded_data is not None:
        if isinstance(decoded_data, str):
            payload_content = decoded_data
        elif isinstance(decoded_data, dict):
            payload_content = decoded_data.get('payload')
        # If decoded_data is some other unexpected type, payload_content remains None

    insert_query = 'INSERT INTO messages VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'
    try:
        insert_params = (
            packet.get('fromId', 'UNK'),
            packet.get('toId', 'UNK'),
            packet.get('id', 'UNK'),
            packet.get('rxSnr'), # Use .get() without default to allow NULL in DB
            packet.get('hopLimit'),
            packet.get('rxRssi'),
            packet.get('hopStart'),
            packet.get('relayNode'),
            payload_content # Use the safely extracted payload
        )
    except Exception as e:
        logger.error(f"Failed to construct insert_params for message: {e}")
        logger.error(f"Packet data that caused the error: {packet}")
        db_conn.close()
        return
    
    with db_conn:
        try:
            db_conn.cursor().execute(insert_query, insert_params)
        except sqlite3.IntegrityError:
            logger.warning(f"Failed to write message to database (IntegrityError, ID '{packet.get('id', 'UNK')}' already exists). Skipping.")
            return
        except sqlite3.OperationalError as e:
            logger.error(f"Unexpected operational error in writing message to database: {e}")
            logger.error(f"Insert query: {insert_query}")
            logger.error(f"Insert parameters: {insert_params}")
            return
    
    logger.info(f"Logged message from {packet.get('fromId', 'UNK')} to {packet.get('toId', 'UNK')}: '{payload_content}'")