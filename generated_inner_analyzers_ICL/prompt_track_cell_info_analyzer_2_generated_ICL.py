
#!/usr/bin/python
# Filename: track_cell_info_analyzer_modified.py
"""
track_cell_info_analyzer_modified.py
An analyzer to process and track LTE RRC messages with additional metrics

Author: Modified
"""

from mobile_insight.analyzer.analyzer import *

__all__ = ["TrackCellInfoAnalyzerModified"]

class TrackCellInfoAnalyzerModified(Analyzer):

    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)

        # Initialize internal states for cell information
        self.cell_info = {
            "dl_freq": None,
            "ul_freq": None,
            "bandwidth": None,
            "tac": None,
            "operator": None
        }
        self.average_freq = None

    def set_source(self, source):
        """
        Set the trace source. Enable the necessary LTE RRC logs.

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)

        source.enable_log("LTE_RRC_Serv_Cell_Info")
        source.enable_log("LTE_RRC_MIB_Packet")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_RRC_Serv_Cell_Info":
            log_item = msg.data.decode()

            # Update cell information
            self.cell_info["dl_freq"] = log_item.get("Downlink frequency", None)
            self.cell_info["ul_freq"] = log_item.get("Uplink frequency", None)
            self.cell_info["bandwidth"] = log_item.get("Bandwidth", None)
            self.cell_info["tac"] = log_item.get("Tracking Area Code", None)
            self.cell_info["operator"] = log_item.get("Operator", None)

            # Calculate and log average frequency
            if self.cell_info["dl_freq"] is not None and self.cell_info["ul_freq"] is not None:
                self.average_freq = (self.cell_info["dl_freq"] + self.cell_info["ul_freq"]) / 2
                self.log_info(f"Average Frequency: {self.average_freq}")

        elif msg.type_id == "LTE_RRC_MIB_Packet":
            log_item = msg.data.decode()

            # Extract MIB-related information
            num_antennas = log_item.get("Number of Antennas", None)
            dl_bandwidth = log_item.get("Downlink Bandwidth", None)
            phy_cell_id = log_item.get("Physical Cell ID", None)

            # Log MIB information
            self.log_info(f"MIB Info - Antennas: {num_antennas}, DL Bandwidth: {dl_bandwidth}, Physical Cell ID: {phy_cell_id}")

    def get_cell_info(self):
        """
        Get the current cell's status.

        :returns: A dictionary containing cell information.
        """
        return self.cell_info

    def get_average_frequency(self):
        """
        Get the average frequency.

        :returns: The average frequency value or None if not available.
        """
        return self.average_freq
