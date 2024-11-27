
#!/usr/bin/python
# Filename: nr_rrc_analyzer_modified.py
"""
A modified NR RRC analyzer.
"""

import xml.etree.ElementTree as ET
from mobile_insight.analyzer.analyzer import *
from mobile_insight.analyzer.protocol_analyzer import *
import time

__all__ = ["NrRrcAnalyzerModified"]

class NrRrcAnalyzerModified(ProtocolAnalyzer):
    """
    A protocol analyzer for NR RRC messages to derive cell configurations and connectivity status.
    """

    def __init__(self):
        print("Init Modified NR RRC Analyzer")
        ProtocolAnalyzer.__init__(self)

        # Initialize packet filters and internal states
        self.add_source_callback(self.__rrc_filter)
        self.__status = NrRrcStatus()  # Current cell status
        self.__history = {}  # Cell history: timestamp -> NrRrcStatus()
        self.__config = {}  # (cell_id, freq) -> NrRrcConfig()

    def __rrc_filter(self, msg):
        """
        Filter all NR RRC packets and process them

        :param msg: the event (message) from the trace collector.
        """
        log_item = msg.data.decode()
        log_item_dict = dict(log_item)

        if msg.type_id == "5G_NR_RRC_OTA_Packet":
            if 'Msg' not in log_item_dict:
                return

            # Update connection status
            self.__update_conn(int(log_item_dict['Freq']), int(log_item_dict['Physical Cell ID']), log_item_dict['timestamp'])

            # Convert message to XML format
            log_xml = ET.XML(log_item_dict['Msg'])
            xml_msg = Event(log_item_dict['timestamp'], msg.type_id, log_xml)

            # Callbacks
            self.__callback_rrc_conn(xml_msg)
            self.__callback_sib_config(xml_msg)
            self.__callback_rrc_reconfig(xml_msg)

            # Raise event to other analyzers
            self.send(xml_msg)

    def __update_conn(self, freq, cid, timestamp):
        """
        Update current cell status based on frequency and cell ID

        :param freq: cell frequency
        :param cid: cell ID
        :param timestamp: message timestamp
        """
        status_updated = False
        if not self.__status.inited():
            status_updated = True
            self.__status.freq = freq
            self.__status.id = cid
        else:
            if self.__status.freq != freq or self.__status.id != cid:
                status_updated = True
                self.__status = NrRrcStatus()
                self.__status.conn = True
                self.__status.freq = freq
                self.__status.id = cid
                self.__history[timestamp] = self.__status

    def __callback_sib_config(self, msg):
        """
        Extract configuration from System Information Blocks (SIBs)

        :param msg: NR RRC SIB messages
        """
        for field in msg.data.iter('field'):
            if field.get('name') == "nr-rrc.sib1_element":
                threshold = None
                for val in field.iter('field'):
                    if val.get('name') == 'nr-rrc.threshold':
                        threshold = int(val.get('show'))
                self.log_info(f"SIB_CONFIG: Threshold={threshold}")

    def __callback_rrc_reconfig(self, msg):
        """
        Extract and log configurations from RRCReconfiguration messages

        :param msg: NR RRC reconfiguration messages
        """
        measobj_id = -1
        report_id = -1

        for field in msg.data.iter('field'):
            if field.get('name') == "nr-rrc.measObjectId":
                measobj_id = int(field.get('show'))

            if field.get('name') == "nr-rrc.reportConfigId":
                report_id = int(field.get('show'))

            if field.get('name') == "nr-rrc.measObjectNR_element":
                ssbFreq = 0
                for val in field.iter('field'):
                    if val.get('name') == 'nr-rrc.ssbFrequency':
                        ssbFreq = val.get('show')

                cur_pair = (self.__status.id, self.__status.freq)
                if cur_pair not in self.__config:
                    self.__config[cur_pair] = NrRrcConfig()
                    self.__config[cur_pair].status = self.__status

                freq = int(ssbFreq) + 10  # Modified calculation
                self.__config[cur_pair].active.measobj[measobj_id] = NrMeasObject(measobj_id, freq)

            if field.get('name') == "nr-rrc.reportConfigNR_element":
                cur_pair = (self.__status.id, self.__status.freq)
                if cur_pair not in self.__config:
                    self.__config[cur_pair] = NrRrcConfig()
                    self.__config[cur_pair].status = self.__status

                hyst = 0
                for val in field.iter('field'):
                    if val.get('name') == 'nr-rrc.hysteresis':
                        hyst = int(val.get('show'))

                report_config = NrReportConfig(report_id, hyst / 1.5)  # Modified hysteresis calculation
                self.__config[cur_pair].active.report_list[report_id] = report_config

    def __callback_rrc_conn(self, msg):
        """
        Update the RRC connectivity status

        :param msg: the RRC message
        """
        for field in msg.data.iter('field'):
            if field.get('name') == "nr-rrc.rrcSetupComplete_element":
                self.__status.conn = True
                self.log_info(self.__status.dump())
            if field.get('name') == "nr-rrc.rrcRelease_element":
                self.__status.conn = False
                self.log_info(self.__status.dump())

    def set_source(self, source):
        """
        Set the trace source and enable the NR RRC messages.

        :param source: the trace source.
        """
        Analyzer.set_source(self, source)
        source.enable_log("5G_NR_RRC_OTA_Packet")

    def get_cell_list(self):
        """
        Get a complete list of cell IDs.

        :returns: a list of cells the device has associated with
        """
        return list(self.__config.keys())

    def get_cell_config(self, cell):
        """
        Return a cell's active/idle-state configuration.

        :param cell: a cell identifier
        :returns: this cell's active/idle-state configurations
        :rtype: NrRrcConfig
        """
        if cell in self.__config:
            return self.__config[cell]
        else:
            return None

    def get_cur_cell_status(self):
        """
        Get current cell's status

        :returns: current cell's status
        :rtype: NrRrcStatus
        """
        return self.__status

    def get_mobility_history(self):
        """
        Get the history of cells the device associates with

        :returns: the cells the device has traversed
        :rtype: a dictionary of timestamp -> NrRrcStatus
        """
        return self.__history


class NrRrcStatus:
    """
    The metadata of a cell, including its ID, frequency band, tracking area code,
    bandwidth, connectivity status, etc.
    """

    def __init__(self):
        self.id = None  # cell ID
        self.freq = None  # cell frequency
        self.rat = "NR"  # radio technology
        self.bandwidth = None  # cell bandwidth
        self.conn = False  # connectivity status (for serving cell only)

    def dump(self):
        """
        Report the cell status

        :returns: a string that encodes the cell status
        """
        return (self.__class__.__name__
                + " cellID=" + str(self.id)
                + " frequency=" + str(self.freq)
                + " bandwidth=" + str(self.bandwidth)
                + " connected=" + str(self.conn))

    def inited(self):
        return (self.id is not None and self.freq is not None)


class NrRrcConfig:
    """
    Per-cell RRC configurations

    The following configurations are supported
        - Active-state
            - Measurement configurations
    """

    def __init__(self):
        self.status = NrRrcStatus()  # the metadata of this cell
        self.status.rat = "NR"
        self.active = NrRrcActive()  # active-state configurations

    def dump(self):
        """
        Report the cell configurations

        :returns: a string that encodes the cell's configurations
        """
        return (self.__class__.__name__ + '\n'
                + self.status.dump()
                + self.active.dump())

    def get_meas_config(self, meas_id):
        """
        Given a meas_id, return the meas_obj and report_config.

        :param meas_id
        :returns: meas_obj and report_config
        """
        if meas_id in self.active.measid_list:
            obj_id, report_id = self.active.measid_list[meas_id]
            if obj_id in self.active.measobj and report_id in self.active.report_list:
                return (self.active.measobj[obj_id], self.active.report_list[report_id])
        return (None, None)


class NrRrcActive:
    """
    RRC active-state configurations (from RRCReconfiguration messsage)
    """

    def __init__(self):
        self.measobj = {}  # meas_id->measobject
        self.report_list = {}  # report_id->reportConfig
        self.measid_list = {}  # meas_id->(obj_id,report_id)

    def dump(self):
        """
        Report the cell's active-state configurations

        :returns: a string that encodes the cell's active-state configurations
        """
        res = ""
        for item in self.measobj:
            res += self.measobj[item].dump()
        for item in self.report_list:
            res += self.report_list[item].dump()
        for item in self.measid_list:
            res += "MeasObj " + str(item) + ' ' + str(self.measid_list[item]) + '\n'
        return res


class NrMeasObject:
    """
    NR Measurement object configuration
    """

    def __init__(self, measobj_id, freq, rat='NR'):
        self.obj_id = measobj_id
        self.freq = freq  # carrier frequency
        self.rat = rat

    def dump(self):
        """
        Report the cell's NR measurement objects

        :returns: a string that encodes the cell's NR measurement objects
        """
        res = (self.__class__.__name__
               + ' object_id=' + str(self.obj_id)
               + ' freq=' + str(self.freq)
               + ' RAT=' + str(self.rat))
        return res


class NrReportConfig:
    """
    NR measurement report configuration
    """

    def __init__(self, report_id, hyst):
        self.report_id = report_id
        self.hyst = hyst
        self.event_list = []

    def add_event(self, event_type, quantity=None, threshold1=None, threshold2=None):
        """
        Add a measurement event

        :param event_type: a measurement type
        :param threshold1: threshold 1
        :param threshold2: threshold 2
        """
        self.event_list.append(NrReportEvent(event_type, quantity, threshold1, threshold2))

    def dump(self):
        """
        Report the cell's measurement report configurations

        :returns: a string that encodes the cell's measurement report configurations
        """
        res = (self.__class__.__name__
               + ' report_id=' + str(self.report_id)
               + ' hyst=' + str(self.hyst))
        for item in self.event_list:
            res += (' ' + str(item.type)
                    + ' ' + str(item.quantity)
                    + ' ' + str(item.threshold1)
                    + ' ' + str(item.threshold2))
        return res


class NrReportEvent:
    """
    Abstraction for NR report event
    """

    def __init__(self, event_type, quantity, threshold1, threshold2=None):
        self.type = event_type
        self.quantity = quantity
        self.threshold1 = threshold1
        self.threshold2 = threshold2
