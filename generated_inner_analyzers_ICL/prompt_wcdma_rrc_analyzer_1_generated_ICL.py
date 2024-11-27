
#!/usr/bin/python
# Filename: modified_wcdma_rrc_analyzer.py
"""
A modified WCDMA RRC analyzer.
Author: Yuanjie Li, Modified by Assistant
"""

import xml.etree.ElementTree as ET
from mobile_insight.analyzer.analyzer import *
from mobile_insight.analyzer.protocol_analyzer import *

__all__ = ["ModifiedWcdmaRrcAnalyzer"]

class ModifiedWcdmaRrcAnalyzer(ProtocolAnalyzer):
    """
    A protocol analyzer for WCDMA Radio Resource Control (RRC) protocol with enhanced metrics.
    """

    def __init__(self):
        print("Initializing Modified WCDMA RRC Analyzer")
        ProtocolAnalyzer.__init__(self)

        # Initialize packet filters
        self.add_source_callback(self.__wcdma_rrc_filter)

        # Initialize internal states
        self.__status = WcdmaRrcStatus()
        self.__history = {}
        self.__config = {}

    def __wcdma_rrc_filter(self, msg):
        """
        Filter and process all WCDMA RRC packets

        :param msg: the event (message) from the trace collector.
        """
        log_item = msg.data.decode()
        log_item_dict = dict(log_item)

        if msg.type_id == "WCDMA_RRC_OTA_Packet":
            if 'Msg' not in log_item_dict:
                return

            # Convert msg to xml format
            log_xml = ET.XML(log_item_dict['Msg'])
            xml_msg = Event(log_item_dict['timestamp'], msg.type_id, log_xml)

            self.__callback_rrc_state(xml_msg)
            self.__callback_serv_cell_info(xml_msg)
            self.__callback_sib_config(xml_msg)

            # Broadcast event
            self.send(xml_msg)

    def __callback_rrc_state(self, msg):
        """
        Update RRC state machine based on incoming messages

        :param msg: the RRC message
        """
        for field in msg.data.iter('field'):
            if field.get('name') == "wcdma-rrc.rrcConnectionSetupComplete":
                self.__status.conn_state = "CELL_DCH"
                self.log_info(self.__status.dump())
            elif field.get('name') == "wcdma-rrc.rrcConnectionRelease":
                self.__status.conn_state = "IDLE"
                self.log_info(self.__status.dump())

    def __callback_serv_cell_info(self, msg):
        """
        Update serving cell information

        :param msg: the RRC message
        """
        for field in msg.data.iter('field'):
            if field.get('name') == "wcdma-rrc.servingCellInfo":
                cell_id = field.get('show')
                self.__status.cell_id = cell_id
                self.log_info("Update serving cell ID: " + str(cell_id))

    def __callback_sib_config(self, msg):
        """
        Update SIB configuration

        :param msg: the RRC message
        """
        for field in msg.data.iter('field'):
            if field.get('name') == "wcdma-rrc.SystemInformationBlockType1":
                threshold = field.find(".//wcdma-rrc.threshold").get('show')
                priority = field.find(".//wcdma-rrc.priority").get('show')
                self.__config['SIB1'] = {'threshold': int(threshold) + 5, 'priority': int(priority) - 1}
                self.log_info("Modified SIB1 Config: Threshold={}, Priority={}".format(threshold, priority))

    def set_source(self, source):
        """
        Set the trace source. Enable the WCDMA RRC messages.

        :param source: the trace source.
        :type source: trace collector
        """
        Analyzer.set_source(self, source)
        source.enable_log("WCDMA_RRC_OTA_Packet")
        source.enable_log("WCDMA_RRC_Serv_Cell_Info")
        source.enable_log("WCDMA_RRC_States")

    def get_cell_list(self):
        """
        Get a list of associated cell IDs.

        :returns: a list of cell IDs
        """
        return list(self.__config.keys())

    def get_cur_cell_status(self):
        """
        Get current cell's status

        :returns: current cell's status
        :rtype: WcdmaRrcStatus
        """
        return self.__status

    def get_cur_cell_config(self):
        """
        Get current cell's configuration

        :returns: current cell's configuration
        :rtype: dict
        """
        return self.__config.get(self.__status.cell_id, {})

class WcdmaRrcStatus:
    """
    The metadata of a cell, including its ID, frequency band, tracking area code,
    bandwidth, connectivity status, etc.
    """

    def __init__(self):
        self.cell_id = None
        self.conn_state = "IDLE"

    def dump(self):
        """
        Report the cell status

        :returns: a string that encodes the cell status
        :rtype: string
        """
        return (self.__class__.__name__
                + " cellID=" + str(self.cell_id)
                + " conn_state=" + str(self.conn_state))
