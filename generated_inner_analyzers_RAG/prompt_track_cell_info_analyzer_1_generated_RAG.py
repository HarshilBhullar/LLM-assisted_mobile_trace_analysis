
#!/usr/bin/python
# Filename: track_cell_info_analyzer_modified.py
"""
Modified TrackCellInfoAnalyzer for LTE RRC analysis with additional metrics.

Author: [Your Name]
"""

from .analyzer import *

import xml.etree.ElementTree as ET

__all__ = ["TrackCellInfoAnalyzerModified"]


class TrackCellInfoAnalyzerModified(Analyzer):
    """
    A modified analyzer for tracking LTE RRC cell information with additional metrics.
    """

    def __init__(self):
        Analyzer.__init__(self)
        self.cell_status = {
            "cell_id": None,
            "tac": None,
            "freq_dl": None,
            "freq_ul": None,
            "bandwidth_dl": None,
            "bandwidth_ul": None,
            "additional_metric": None
        }
        self.add_source_callback(self.__rrc_filter)

    def set_source(self, source):
        """
        Set the trace source. Enable LTE RRC messages.

        :param source: the trace source.
        :type source: trace collector
        """
        Analyzer.set_source(self, source)
        source.enable_log("LTE_RRC_Serv_Cell_Info")
        source.enable_log("LTE_RRC_MIB_Packet")

    def __rrc_filter(self, event):
        if event.type_id == "LTE_RRC_Serv_Cell_Info":
            self.__callback_serv_cell(event)
        elif event.type_id == "LTE_RRC_MIB_Packet":
            self.__callback_mib_cell(event)

    def __callback_serv_cell(self, event):
        log_item = event.data
        if "Cell Identity" in log_item:
            self.cell_status["cell_id"] = log_item["Cell Identity"]
        if "TAC" in log_item:
            self.cell_status["tac"] = log_item["TAC"]
        if "DL Freq" in log_item:
            self.cell_status["freq_dl"] = log_item["DL Freq"]
        if "UL Freq" in log_item:
            self.cell_status["freq_ul"] = log_item["UL Freq"]
        if "DL Bandwidth" in log_item:
            self.cell_status["bandwidth_dl"] = log_item["DL Bandwidth"]
        if "UL Bandwidth" in log_item:
            self.cell_status["bandwidth_ul"] = log_item["UL Bandwidth"]

        # Calculate additional metric
        if self.cell_status["bandwidth_dl"] is not None and self.cell_status["bandwidth_ul"] is not None:
            self.cell_status["additional_metric"] = self.cell_status["bandwidth_dl"] + self.cell_status["bandwidth_ul"]
            self.log_info(f"Additional Metric: {self.cell_status['additional_metric']}")

    def __callback_mib_cell(self, event):
        log_item = event.data
        log_xml = ET.XML(log_item["Msg"])
        
        for val in log_xml.iter("field"):
            if val.get("name") == "lte-rrc.numOfAntennaPorts":
                num_antennas = val.get("show")
                self.log_info(f"Number of Antennas: {num_antennas}")
            if val.get("name") == "lte-rrc.dl_Bandwidth":
                self.cell_status["bandwidth_dl"] = val.get("show")
            if val.get("name") == "lte-rrc.ul_Bandwidth":
                self.cell_status["bandwidth_ul"] = val.get("show")

    def get_cell_id(self):
        return self.cell_status["cell_id"]

    def get_tac(self):
        return self.cell_status["tac"]

    def get_freq_dl(self):
        return self.cell_status["freq_dl"]

    def get_freq_ul(self):
        return self.cell_status["freq_ul"]

    def get_bandwidth_dl(self):
        return self.cell_status["bandwidth_dl"]

    def get_bandwidth_ul(self):
        return self.cell_status["bandwidth_ul"]

    def get_additional_metric(self):
        return self.cell_status["additional_metric"]
