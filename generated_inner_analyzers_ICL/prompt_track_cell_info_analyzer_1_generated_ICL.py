
#!/usr/bin/python
# Filename: track_cell_info_analyzer_modified.py
"""
A modified analyzer for tracking LTE cell information with additional metrics.

Author: [Your Name]
"""

from mobile_insight.analyzer.analyzer import *
import xml.etree.ElementTree as ET

__all__ = ["TrackCellInfoAnalyzerModified"]

class LteRrcStatus:
    def __init__(self):
        self.id = None  # cell ID
        self.freq_dl = None  # downlink frequency
        self.freq_ul = None  # uplink frequency
        self.tac = None  # tracking area code
        self.bandwidth_dl = None  # downlink bandwidth
        self.bandwidth_ul = None  # uplink bandwidth
        self.operator = None  # operator MNC
        self.additional_metric = None  # Additional metric

    def inited(self):
        return (self.id is not None and self.freq_dl is not None)

    def dump(self):
        return (f"LteRrcStatus: cellID={self.id}, freq_dl={self.freq_dl}, "
                f"freq_ul={self.freq_ul}, TAC={self.tac}, bandwidth_dl={self.bandwidth_dl}, "
                f"bandwidth_ul={self.bandwidth_ul}, operator={self.operator}, "
                f"additional_metric={self.additional_metric}")

class TrackCellInfoAnalyzerModified(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.__status = LteRrcStatus()
        self.add_source_callback(self.__rrc_filter)

    def set_source(self, source):
        Analyzer.set_source(self, source)
        source.enable_log("LTE_RRC_Serv_Cell_Info")
        source.enable_log("LTE_RRC_MIB_Packet")

    def __rrc_filter(self, msg):
        if msg.type_id == "LTE_RRC_Serv_Cell_Info":
            self.__callback_serv_cell(msg)
        elif msg.type_id == "LTE_RRC_MIB_Packet":
            self.__callback_mib_cell(msg)

    def __callback_serv_cell(self, msg):
        log_item = msg.data.decode()
        if not self.__status.inited():
            self.__status.freq_dl = log_item['Downlink frequency']
            self.__status.id = log_item['Cell ID']
            self.__status.tac = log_item['TAC']
            self.__status.operator = log_item['MNC']
            self.__status.freq_ul = log_item.get('Uplink frequency', None)
            self.__status.bandwidth_dl = log_item.get('DL Bandwidth', None)
            self.__status.bandwidth_ul = log_item.get('UL Bandwidth', None)
            self.__calculate_additional_metric()

        self.log_info(self.__status.dump())

    def __callback_mib_cell(self, msg):
        log_item = msg.data.decode()
        if not self.__status.inited():
            self.__status.bandwidth_dl = log_item.get('DL Bandwidth', None)
            self.__calculate_additional_metric()

    def __calculate_additional_metric(self):
        if self.__status.bandwidth_dl and self.__status.bandwidth_ul:
            self.__status.additional_metric = (self.__status.bandwidth_dl + self.__status.bandwidth_ul) / 2
            self.log_info(f"Calculated Additional Metric: {self.__status.additional_metric}")

    def get_cur_cell_id(self):
        return self.__status.id

    def get_cur_tac(self):
        return self.__status.tac

    def get_cur_freq_dl(self):
        return self.__status.freq_dl

    def get_cur_freq_ul(self):
        return self.__status.freq_ul

    def get_cur_bandwidth_dl(self):
        return self.__status.bandwidth_dl

    def get_cur_bandwidth_ul(self):
        return self.__status.bandwidth_ul

    def get_additional_metric(self):
        return self.__status.additional_metric
