import contextlib
import os
import sys
import time
import logging 

import utils

import meshtastic
import meshtastic.serial_interface
from pubsub import pub

VIEW_ALL_NODES = False
LISTEN = True

#global logger
log_level = logging.INFO
logger = utils.logging_setup(__name__, log_level=log_level)
utils.logger_initialize_msg(logger, __name__, logging.DEBUG)

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
    print(f"Received: {packet}")

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

def main():
    
    # By default will try to find a meshtastic device, otherwise provide a device path like /dev/ttyUSB0
    interface = meshtastic.serial_interface.SerialInterface()
    
    pub.subscribe(onReceive, "meshtastic.receive")
    pub.subscribe(onConnection, "meshtastic.connection.established")

    with open('desired_nodes.info') as fp:
        desired_nodes = [node.strip().split(',') 
                        for node in fp.readlines()]

    with nostdout(): 
        data_table = interface.showNodes(True, None)
    nodes = parse_data_table(data_table)

    print("Read {} nodes from input list".format(len(desired_nodes)))
    for desired_node in desired_nodes:
        print('\t{}'.format(desired_node[0]))
    print("Found {} nodes on local mesh".format(len(nodes)))
    if VIEW_ALL_NODES:
        for node in nodes:
            print('\t{}'.format(node[2]))

    print("MATCHES")
    for desired_node in desired_nodes:
        for node in nodes:
            if node[2] == desired_node[0]: 
                print("Node {} ({}):".format(desired_node[0], desired_node[1]))
                pprint_node_entry(node)

    if LISTEN:
        logger.info("Listening...")
        try:
            while True:
                time.sleep(1000)
        except KeyboardInterrupt:
            logger.info("Exiting due to keyboard interrupt")

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
    #data_table = interface.showNodes(True, ['user.id', 'user.longName', 'user.hwModel'])

if __name__ == '__main__':
    main()