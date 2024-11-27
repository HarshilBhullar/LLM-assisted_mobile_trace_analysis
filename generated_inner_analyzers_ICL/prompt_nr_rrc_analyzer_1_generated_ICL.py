
#!/usr/bin/python
# Filename: nr_rrc_analyzer_modified.py
"""
A modified NR RRC analyzer for enhanced analysis on NR RRC packets.

Author: Yuanjie Li, Zhehui Zhang
"""

import xml.etree.ElementTree as ET
from .analyzer import *
from .state_machine import *
from .protocol_analyzer import *
import timeit
import time

from .profile import Profile, ProfileHierarchy

__all__ = ["NrRrcAnalyzerModified"]

class NrRrcAnalyzerModified(ProtocolAnalyzer):
    """
    A modified protocol analyzer for NR Radio Resource Control (RRC) protocol.
    """

    def __init__(self):
        print("Init Modified NR RRC Analyzer")
        ProtocolAnalyzer.__init__(self)

        # init packet filters
        self.add_source_callback(self.__rrc_filter)

        # init internal states
        self.__status = NrRrcStatus()  # current cell status
        self.__history = {}  # cell history: timestamp -> NrRrcStatus()
        self.__config = {}  # (cell_id,freq) -> NrRrcConfig()

    def __rrc_filter(self, msg):
        """
        Filter all NR RRC packets, and call functions to process it

        :param msg: the event (message) from the trace collector.
        """
        if msg.type_id == "5G_NR_RRC_OTA_Packet":
            log_item = msg.data.decode()
            log_item_dict = dict(log_item)

            # Convert msg to xml format
            log_xml = ET.XML(log_item_dict['Msg'])
            xml_msg = Event(log_item_dict['timestamp'], msg.type_id, log_xml)

            self.__callback_rrc_conn(xml_msg)
            self.__callback_rrc_reconfig(xml_msg)

            self.send(xml_msg)

    def __callback_rrc_conn(self, msg):
        """
        Update the connectivity status based on RRC Setup Complete and RRC Release messages.

        :param msg: NR RRC OTA messages
        """
        for field in msg.data.iter('field'):
            if field.get('name') == "nr-rrc.rrcConnectionSetupComplete_element":
                self.__status.update_connection_status("CONNECTED")
                self.log_info("RRC Connection Setup Complete")
            elif field.get('name') == "nr-rrc.rrcConnectionRelease_element":
                self.__status.update_connection_status("IDLE")
                self.log_info("RRC Connection Released")

    def __callback_rrc_reconfig(self, msg):
        """
        Extract measurement and report configurations from RRC Reconfiguration messages.

        :param msg: NR RRC reconfiguration messages
        """
        for field in msg.data.iter('field'):
            if field.get('name') == "nr-rrc.RRCReconfiguration_element":
                self.log_info("RRC Reconfiguration Received")
                # Extract and update internal configurations
                # Placeholder for future implementation

    def set_source(self, source):
        """
        Set the trace source. Enable the NR RRC messages.

        :param source: the trace source.
        :type source: trace collector
        """
        Analyzer.set_source(self, source)
        source.enable_log("5G_NR_RRC_OTA_Packet")

class NrRrcStatus:
    """
    An abstraction to maintain the NR RRC status.
    """
    def __init__(self):
        self.connection_status = "IDLE"

    def update_connection_status(self, status):
        self.connection_status = status

    def dump(self):
        return f"Connection Status: {self.connection_status}"
