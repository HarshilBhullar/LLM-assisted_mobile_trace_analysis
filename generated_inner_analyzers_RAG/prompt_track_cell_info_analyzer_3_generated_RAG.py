
#!/usr/bin/python
# Filename: track_cell_info_analyzer_modified.py
"""
A modified LTE RRC analyzer for tracking cell information.

Author: Yuanjie Li, Zhehui Zhang
Modified by: [Your Name]
"""

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from .analyzer import Analyzer

__all__ = ["TrackCellInfoAnalyzerModified"]

class TrackCellInfoAnalyzerModified(Analyzer):
    """
    A protocol analyzer for LTE Radio Resource Control (RRC) protocol.
    """

    def __init__(self):
        Analyzer.__init__(self)
        self.__status = LteRrcStatus()  # current cell status
        self.add_source_callback(self.__rrc_filter)

    def set_source(self, source):
        """
        Set the trace source. Enable the LTE RRC messages.

        :param source: the trace source.
        :type source: trace collector
        """
        Analyzer.set_source(self, source)
        source.enable_log("LTE_RRC_Serv_Cell_Info")
        source.enable_log("LTE_RRC_MIB_Packet")

    def __rrc_filter(self, msg):
        """
        Filter all LTE RRC packets, and call functions to process it.

        :param msg: the event (message) from the trace collector.
        """
        if msg.type_id == "LTE_RRC_Serv_Cell_Info":
            self.__callback_serv_cell(msg)
        elif msg.type_id == "LTE_RRC_MIB_Packet":
            self.__callback_mib_cell(msg)

    def __callback_serv_cell(self, msg):
        """
        A callback to update current cell status using LTE_RRC_Serv_Cell_Info message.

        :param msg: the RRC messages with cell status
        """
        log_item = msg.data.decode()
        log_item_dict = dict(log_item)

        status_updated = False
        if not self.__status.inited():
            self.__status.dl_freq = log_item_dict['Downlink frequency']
            self.__status.ul_freq = log_item_dict['Uplink frequency']
            self.__status.bandwidth = log_item_dict['Bandwidth']
            self.__status.cell_id = log_item_dict['Cell ID']
            self.__status.tac = log_item_dict['TAC']
            self.__status.operator = self.__get_operator(log_item_dict['MNC'])
            status_updated = True

        else:
            if self.__status.dl_freq != log_item_dict['Downlink frequency'] or \
               self.__status.cell_id != log_item_dict['Cell ID'] or \
               self.__status.tac != log_item_dict['TAC']:
                self.__status = LteRrcStatus()
                self.__status.dl_freq = log_item_dict['Downlink frequency']
                self.__status.ul_freq = log_item_dict['Uplink frequency']
                self.__status.bandwidth = log_item_dict['Bandwidth']
                self.__status.cell_id = log_item_dict['Cell ID']
                self.__status.tac = log_item_dict['TAC']
                self.__status.operator = self.__get_operator(log_item_dict['MNC'])
                status_updated = True

        if status_updated:
            self.log_info(self.__status.dump())

    def __callback_mib_cell(self, msg):
        """
        A callback to process LTE_RRC_MIB_Packet to extract MIB information.

        :param msg: the RRC MIB messages
        """
        log_item = msg.data.decode()
        log_item_dict = dict(log_item)

        self.__status.mib_antenna = log_item_dict.get('Number of antennas', None)
        self.__status.mib_dl_bandwidth = log_item_dict.get('Downlink bandwidth', None)
        self.log_info("Updated MIB information: " + str(self.__status.mib_antenna) + ", " + str(self.__status.mib_dl_bandwidth))

    def __get_operator(self, mnc):
        """
        Determine the operator based on the MNC value.

        :param mnc: Mobile Network Code
        :returns: Operator name
        """
        operators = {
            '001': 'Operator A',
            '002': 'Operator B',
            '003': 'Operator C'
            # Add other MNC-operator mappings as needed
        }
        return operators.get(mnc, 'Unknown')

    def get_cell_info(self):
        """
        Get current cell information.

        :returns: a dictionary of current cell information
        """
        return {
            'cell_id': self.__status.cell_id,
            'tac': self.__status.tac,
            'dl_freq': self.__status.dl_freq,
            'ul_freq': self.__status.ul_freq,
            'bandwidth': self.__status.bandwidth,
            'operator': self.__status.operator,
            'mib_antenna': self.__status.mib_antenna,
            'mib_dl_bandwidth': self.__status.mib_dl_bandwidth
        }


class LteRrcStatus:
    """
    The metadata of a cell, including its ID, frequency band, bandwidth,
    operator, connectivity status, etc.
    """
    def __init__(self):
        self.cell_id = None
        self.dl_freq = None
        self.ul_freq = None
        self.bandwidth = None
        self.tac = None
        self.operator = None
        self.mib_antenna = None
        self.mib_dl_bandwidth = None

    def dump(self):
        """
        Report the cell status.

        :returns: a string that encodes the cell status
        :rtype: string
        """
        return (self.__class__.__name__ +
                ' cellID=' + str(self.cell_id) +
                ' dl_freq=' + str(self.dl_freq) +
                ' ul_freq=' + str(self.ul_freq) +
                ' bandwidth=' + str(self.bandwidth) +
                ' TAC=' + str(self.tac) +
                ' operator=' + str(self.operator) + '\n')

    def inited(self):
        return self.cell_id is not None and self.dl_freq is not None
