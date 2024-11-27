
#!/usr/bin/python
# Filename: track_cell_info_analyzer_modified.py
"""
A modified analyzer to track LTE RRC protocol cell information

Author: Yuanjie Li
"""

from mobile_insight.analyzer.analyzer import *

__all__ = ["TrackCellInfoAnalyzerModified"]


class LteRrcStatus:
    def __init__(self):
        self.dl_freq = None
        self.ul_freq = None
        self.dl_bandwidth = None
        self.ul_bandwidth = None
        self.cell_id = None
        self.tac = None
        self.operator = None
        self.initialized = False

    def update(self, dl_freq=None, ul_freq=None, dl_bandwidth=None, ul_bandwidth=None, cell_id=None, tac=None, operator=None):
        self.dl_freq = dl_freq or self.dl_freq
        self.ul_freq = ul_freq or self.ul_freq
        self.dl_bandwidth = dl_bandwidth or self.dl_bandwidth
        self.ul_bandwidth = ul_bandwidth or self.ul_bandwidth
        self.cell_id = cell_id or self.cell_id
        self.tac = tac or self.tac
        self.operator = operator or self.operator
        self.initialized = True


class TrackCellInfoAnalyzerModified(Analyzer):

    def __init__(self):
        Analyzer.__init__(self)
        self.cell_status = LteRrcStatus()
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
        dl_freq = log_item.get("Downlink frequency")
        ul_freq = log_item.get("Uplink frequency")
        dl_bandwidth = log_item.get("DL bandwidth")
        ul_bandwidth = log_item.get("UL bandwidth")
        cell_id = log_item.get("Cell ID")
        tac = log_item.get("TAC")
        mnc = log_item.get("MNC")
        operator = self.__get_operator_from_mnc(mnc)
        
        if not self.cell_status.initialized or dl_freq != self.cell_status.dl_freq or \
                cell_id != self.cell_status.cell_id or tac != self.cell_status.tac:
            self.cell_status.update(dl_freq, ul_freq, dl_bandwidth, ul_bandwidth, cell_id, tac, operator)
            self.log_info("Updated cell status: DL Freq={}, UL Freq={}, DL BW={}, UL BW={}, Cell ID={}, TAC={}, Operator={}".format(
                dl_freq, ul_freq, dl_bandwidth, ul_bandwidth, cell_id, tac, operator))

    def __callback_mib_cell(self, msg):
        log_item = msg.data.decode()
        num_antennas = log_item.get("Number of antennas")
        dl_bandwidth = log_item.get("DL bandwidth")
        self.cell_status.update(dl_bandwidth=dl_bandwidth)
        self.log_info("MIB info: Number of antennas={}, DL Bandwidth={}".format(num_antennas, dl_bandwidth))

    def __get_operator_from_mnc(self, mnc):
        mnc_operator_mapping = {
            "01": "AT&T",
            "02": "Verizon",
            "03": "T-Mobile"
        }
        return mnc_operator_mapping.get(mnc, "Unknown")

    def get_cell_id(self):
        return self.cell_status.cell_id

    def get_tac(self):
        return self.cell_status.tac

    def get_dl_freq(self):
        return self.cell_status.dl_freq

    def get_ul_freq(self):
        return self.cell_status.ul_freq

    def get_dl_bandwidth(self):
        return self.cell_status.dl_bandwidth

    def get_ul_bandwidth(self):
        return self.cell_status.ul_bandwidth

    def get_operator(self):
        return self.cell_status.operator
