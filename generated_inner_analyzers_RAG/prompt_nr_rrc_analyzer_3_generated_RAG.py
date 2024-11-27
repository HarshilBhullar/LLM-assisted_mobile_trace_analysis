
#!/usr/bin/python
# Filename: nr_rrc_analyzer_modified.py
"""
A modified NR RRC analyzer for 5G cellular networks.
Author: Yuanjie Li
"""

import xml.etree.ElementTree as ET
from mobile_insight.analyzer.analyzer import *
from mobile_insight.analyzer.state_machine import *
from mobile_insight.analyzer.protocol_analyzer import *
import time

__all__ = ["NrRrcAnalyzerModified"]

class NrRrcAnalyzerModified(ProtocolAnalyzer):
    """
    A protocol analyzer for NR Radio Resource Control (RRC) protocol.
    """

    def __init__(self):
        ProtocolAnalyzer.__init__(self)
        self.add_source_callback(self.__rrc_filter)

        # Initiate internal states
        self.__status = NrRrcStatus()  # current cell status
        self.__history = {}  # cell history: timestamp -> NrRrcStatus()
        self.__config = {}  # (cell_id, freq) -> NrRrcConfig()

    def __rrc_filter(self, msg):
        """
        Filter all NR RRC packets, and call functions to process them.

        :param msg: the event (message) from the trace collector.
        """
        log_item = msg.data.decode()
        log_item_dict = dict(log_item)

        self.send_to_coordinator(Event(msg.timestamp, msg.type_id, str(log_item)))

        if msg.type_id == "5G_NR_RRC_OTA_Packet":
            if 'Msg' not in log_item_dict:
                return

            # Convert msg to xml format
            log_xml = ET.XML(log_item_dict['Msg'])
            xml_msg = Event(log_item_dict['timestamp'], msg.type_id, log_xml)

            self.__callback_rrc_conn(xml_msg)
            self.__callback_sib_config(xml_msg)
            self.__callback_rrc_reconfig(xml_msg)

            self.send(xml_msg)

    def __callback_sib_config(self, msg):
        """
        Extract configurations from System Information Blocks (SIBs),
        including threshold settings and preference configurations.

        :param msg: RRC SIB messages
        """
        for field in msg.data.iter('field'):
            if field.get('name') == "nr-rrc.sib1_element":
                sib1_config = {}
                sib1_config['timestamp'] = str(msg.timestamp)
                for val in field.iter('field'):
                    if val.get('name') == 'nr-rrc.cellSelectionInfo':
                        sib1_config['cellSelectionInfo'] = val.get('show')
                self.broadcast_info('SIB1_CONFIG', sib1_config)
                self.log_info('SIB1_CONFIG: ' + str(sib1_config))

    def __callback_rrc_reconfig(self, msg):
        """
        Extract configurations from RRCReconfiguration Message,
        including measurement profiles and report configurations.

        :param msg: NR RRC reconfiguration messages
        """
        for field in msg.data.iter('field'):
            if field.get('name') == "nr-rrc.rrcReconfiguration_element":
                reconfig_info = {}
                reconfig_info['timestamp'] = str(msg.timestamp)
                for val in field.iter('field'):
                    if val.get('name') == 'nr-rrc.measConfig':
                        reconfig_info['measConfig'] = val.get('show')
                self.broadcast_info('RRC_RECONFIG', reconfig_info)
                self.log_info('RRC_RECONFIG: ' + str(reconfig_info))

    def __callback_rrc_conn(self, msg):
        """
        Update and log the RRC connectivity status based on message content.

        :param msg: NR RRC connection messages
        """
        for field in msg.data.iter('field'):
            if field.get('name') == "nr-rrc.rrcConnectionSetupComplete_element":
                self.__update_conn(msg, field)

    def __update_conn(self, msg, field):
        """
        Update the current cell status based on frequency and cell ID.

        :param msg: NR RRC connection messages
        :param field: The specific field containing frequency and cell ID info
        """
        conn_status = {}
        conn_status['timestamp'] = str(msg.timestamp)
        conn_status['cell_id'] = field.get('show')
        self.__status.update(conn_status['cell_id'])
        self.broadcast_info('RRC_CONN', conn_status)
        self.log_info('RRC_CONN: ' + str(conn_status))

    def get_cell_list(self):
        """
        Return a list of all cell IDs associated with the device.

        :returns: List of cell IDs
        """
        return list(self.__history.keys())

    def get_cell_config(self, cell_id):
        """
        Retrieve the configuration for a given cell.

        :param cell_id: The cell ID to query
        :returns: Cell configuration
        """
        return self.__config.get(cell_id, None)

    def get_cur_cell_status(self):
        """
        Return the current cell's connectivity status and configuration.

        :returns: Current cell status
        """
        return self.__status

    def get_mobility_history(self):
        """
        Provide a history of all cells the device has been connected to.

        :returns: Cell history
        """
        return self.__history

class NrRrcStatus:
    """
    An abstraction to maintain the NR RRC status.
    """
    def __init__(self):
        self.cell_id = None

    def update(self, cell_id):
        self.cell_id = cell_id

    def dump(self):
        return f"NR RRC Status: Cell ID = {self.cell_id}"
