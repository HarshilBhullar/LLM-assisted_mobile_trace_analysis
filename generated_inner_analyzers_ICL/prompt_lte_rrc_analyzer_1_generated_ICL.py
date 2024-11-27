
#!/usr/bin/python
# Filename: lte_rrc_analyzer_modified.py
"""
lte_rrc_analyzer_modified.py
A modified LTE RRC protocol analyzer with additional metrics.

Author: Yuanjie Li, Modified by: Assistant
"""

from mobile_insight.analyzer import ProtocolAnalyzer
from mobile_insight.analyzer.analyzer import Event

__all__ = ["LteRrcAnalyzerModified"]

class LteRrcAnalyzerModified(ProtocolAnalyzer):
    
    def __init__(self):
        ProtocolAnalyzer.__init__(self)
        
        self.state = "RRC_IDLE"
        self.current_cell_status = {}
        self.cell_history = []
        self.configurations = {}

        self.add_source_callback(self.__rrc_filter)

    def set_source(self, source):
        ProtocolAnalyzer.set_source(self, source)
        source.enable_log("LTE_RRC_OTA_Packet")
        source.enable_log("LTE_RRC_Serv_Cell_Info")
        source.enable_log("LTE_RRC_CDRX_Events_Info")

    def __rrc_filter(self, msg):
        if msg.type_id == "LTE_RRC_OTA_Packet":
            self.__callback_rrc_ota(msg)
        elif msg.type_id == "LTE_RRC_Serv_Cell_Info":
            self.__callback_serv_cell(msg)
        elif msg.type_id == "LTE_RRC_CDRX_Events_Info":
            self.__callback_cd_rx_events(msg)

    def __callback_rrc_ota(self, msg):
        # Process RRC OTA messages and handle state transitions
        if "RRCConnectionSetupComplete" in msg.data.decode():
            self.state = "RRC_CONNECTED"
            self.log_info("Transition to RRC_CONNECTED")
        elif "RRCConnectionRelease" in msg.data.decode():
            self.state = "RRC_IDLE"
            self.log_info("Transition to RRC_IDLE")
        self.broadcast_info("RRC_STATE", {"state": self.state})

    def __callback_serv_cell(self, msg):
        # Update current cell status based on service cell info
        serv_cell_info = msg.data.decode()
        self.current_cell_status.update(serv_cell_info)
        self.cell_history.append(self.current_cell_status.copy())
        self.broadcast_info("CELL_STATUS", self.current_cell_status)

    def __callback_cd_rx_events(self, msg):
        # Process CDRX events and extract relevant metrics
        cd_rx_data = msg.data.decode()
        self.log_info(f"CDRX Event: {cd_rx_data}")

    def create_state_machine(self):
        # Define state transitions and conditions for RRC states
        pass  # Define transitions and logic here

    def __callback_sib_config(self, msg):
        # Extract configurations from SIB messages
        sib_config_data = msg.data.decode()
        self.configurations.update(sib_config_data)
        self.broadcast_info("SIB_CONFIG", self.configurations)

    def __callback_rrc_reconfig(self, msg):
        # Process RRC Reconfiguration messages
        reconfig_data = msg.data.decode()
        self.configurations.update(reconfig_data)
        self.broadcast_info("RRC_RECONFIG", self.configurations)
