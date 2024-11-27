
#!/usr/bin/python
# Filename: wcdma_rrc_analyzer_modified.py

"""
A modified analyzer for WCDMA RRC protocol

Author: [Your Name]
"""

from mobile_insight.analyzer.analyzer import ProtocolAnalyzer
import datetime

__all__ = ["WcdmaRrcAnalyzerModified"]

class WcdmaRrcAnalyzerModified(ProtocolAnalyzer):
    """
    A modified analyzer for WCDMA RRC protocol to analyze and modify metrics
    """

    def __init__(self):
        ProtocolAnalyzer.__init__(self)

        # Initialize state machine and internal status
        self.state_machine = {
            "IDLE": "CELL_FACH",
            "CELL_FACH": "CELL_DCH",
            "CELL_DCH": "URA_PCH",
            "URA_PCH": "CELL_PCH",
            "CELL_PCH": "IDLE"
        }
        self.current_state = "IDLE"
        self.cell_status = {}
        self.cell_history = []
        self.configurations = {}

        # Set up packet filters
        self.add_source_callback(self.__rrc_filter)

    def set_source(self, source):
        ProtocolAnalyzer.set_source(self, source)
        # Enable necessary logs
        source.enable_log("WCDMA_RRC_Serv_Cell_Info")
        source.enable_log("WCDMA_RRC_States")
        source.enable_log("WCDMA_RRC_OTA_Packet")

    def __rrc_filter(self, msg):
        if msg.type_id == "WCDMA_RRC_Serv_Cell_Info":
            self.__callback_serv_cell(msg)
        elif msg.type_id == "WCDMA_RRC_States":
            self.__callback_rrc_state(msg)
        elif msg.type_id == "WCDMA_RRC_OTA_Packet":
            self.__callback_sib_config(msg)

    def __callback_serv_cell(self, msg):
        data = msg.data.decode()
        self.cell_status.update({
            "cell_id": data.get("Cell ID"),
            "frequency": data.get("UARFCN DL") * 2,  # Modified frequency
            "psc": data.get("Primary Scrambling Code")
        })
        self.cell_history.append(self.cell_status.copy())

    def __callback_rrc_state(self, msg):
        data = msg.data.decode()
        new_state = data.get("RRC State")
        if new_state in self.state_machine:
            self.current_state = self.state_machine[new_state]

    def __callback_sib_config(self, msg):
        data = msg.data.decode()
        for sib in data.get("SIBs", []):
            if sib.get("SIB Type") == "SIB3":
                self.configurations["intra_freq"] = sib.get("IntraFreqMeasurement", {}).get("Measurement Quantity") * 1.5  # Modified threshold
            elif sib.get("SIB Type") == "SIB5":
                self.configurations["inter_freq"] = sib.get("InterFreqMeasurement", {}).get("Measurement Quantity") * 1.2  # Modified threshold

    def report_cell_status(self):
        return str(self.cell_status)

    def report_configurations(self):
        return str(self.configurations)

    def create_profile_hierarchy(self):
        profile = {
            "Serving Cell": self.cell_status,
            "Configuration": self.configurations
        }
        return profile

    def dump(self):
        return {
            "Current State": self.current_state,
            "Cell Status": self.report_cell_status(),
            "Configurations": self.report_configurations()
        }
