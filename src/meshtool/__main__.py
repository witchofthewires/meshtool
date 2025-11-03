import contextlib
import os
import sys
import time
import logging 
import yaml
import argparse

from .utils import logging_setup, logger_initialize_msg
from .db import create_meshdb, add_message_entry, add_node_entry
from ._version import __version__

import meshtastic
import meshtastic.serial_interface
from pubsub import pub

#global logger
log_level = logging.INFO
logger = logging_setup(__name__, log_level=log_level)
logger_initialize_msg(logger, __name__, logging.DEBUG)

global MESHDB_NAME

# https://stackoverflow.com/a/2829036 for context template
# https://stackoverflow.com/a/45669280 for devnull
@contextlib.contextmanager
def nostdout():
    save_stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w', encoding='utf-16')
    yield
    sys.stdout.close()
    sys.stdout = save_stdout

# fields taken from meshtastic/mesh_interface.py lines 237-254
def pprint_node_entry(node):
    fields = [
                "User",
                "ID",
                "AKA",
                "Hardware",
                "Pubkey",
                "Role",
                "Latitude",
                "Longitude",
                "Altitude",
                "Battery",
                "Channel util.",
                "Tx air util.",
                "SNR",
                "Hops",
                "Channel",
                "LastHeard",
                "Since",        
              ]
    # first value of 'node' is meshtastic SDK table ID, not relevant
    for name, value in zip(fields, node[1:]):
        print("\t{}: {}".format(name, value))

def onReceive(packet, interface): # called when a packet arrives
    # must be db_name, not db_conn, to avoid thread-level errors
    add_message_entry(MESHDB_NAME, packet) 

def onConnection(interface, topic=pub.AUTO_TOPIC): # called when we (re)connect to the radio
    # defaults to broadcast, specify a destination ID if you wish
    interface.sendText("hello mesh")

def parse_data_table(data_table):
    nodes = []
    rows = [row for row in data_table.split('\n') if row[1] == ' ']
    for row in rows[1:]: # first row is headers
        nodes.append([field.strip() 
                      for field in row.split('│') # │!=| (character is not standard pipe)
                      if field.strip() != ''])
    return nodes

def get_interface():
    # By default will try to find a meshtastic device, otherwise provide a device path like /dev/ttyUSB0
    return meshtastic.serial_interface.SerialInterface()

def list_available_interfaces():
    return meshtastic.util.findPorts(eliminate_duplicates=True)

def main():

    parser = argparse.ArgumentParser(description='Meshtastic CLI utility')
    parser.add_argument('-f', '--file', type=str,
                    help='Path to YAML configuration file')
    parser.add_argument('--version', action='store_true',
                    help='Display current version')
    parser.add_argument('-p', '--ports', action='store_true',
                    help='List available serial ports')
    args = parser.parse_args()
    args.file = './default.config.yaml' if not args.file else args.file

    try:
        with open(args.file) as f:
            cfg = yaml.load(f, Loader=yaml.FullLoader)
            db_name = cfg['db_name']# if args.db_name is None else args.db_name
            view_all_nodes = cfg['view_all_nodes']
            listen = cfg['listen']
    except FileNotFoundError:            
        logger.error("Failed to load YAML config file!")
        exit(1)
    
    if args.version:
        print(f"Meshtastic v{__version__}")
        sys.exit(0)
    elif args.ports:
        print(list_available_interfaces())
        sys.exit(0)

    # load db
    global MESHDB_NAME 
    MESHDB_NAME = db_name
    db_conn = create_meshdb(db_name)

    interface = get_interface()
    
    pub.subscribe(onReceive, "meshtastic.receive")
    pub.subscribe(onConnection, "meshtastic.connection.established")

    with open('desired_nodes.info') as fp:
        desired_nodes = [node.strip().split(',') 
                        for node in fp.readlines()]

    with nostdout(): 
        data_table = interface.showNodes(True, None)
    nodes = parse_data_table(data_table)

    logger.debug("Read {} nodes from input list".format(len(desired_nodes)))
    for desired_node in desired_nodes:
        logger.debug('\t{}'.format(desired_node[0]))
    logger.info("Found {} nodes on local mesh".format(len(nodes)))

    if view_all_nodes:
        for node in nodes:
            logger.debug('\t{}'.format(node[2]))

    # details of detected nodes from input list
    for desired_node in desired_nodes:
        for node in nodes:
            if node[2] == desired_node[0]: 
                logger.info("Node {} ({}) detected at {}:".format(desired_node[0], desired_node[1], node[-2]))
                pprint_node_entry(node)
                add_node_entry(db_conn, node)

    if listen:
        logger.info("Listening...")
        try:
            while True:
                time.sleep(1000)
        except KeyboardInterrupt:
            logger.info("Exiting due to keyboard interrupt")

if __name__ == '__main__':
    main()
