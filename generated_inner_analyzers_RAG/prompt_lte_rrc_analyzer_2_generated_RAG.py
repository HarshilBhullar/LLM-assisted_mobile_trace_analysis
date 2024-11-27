
#!/usr/bin/python
# Filename: lte_rrc_analyzer_modified.py
"""
A modified LTE RRC analyzer with enhanced state management and message handling

Author: Yuanjie Li, Modified by OpenAI
"""

from mobile_insight.analyzer.protocol_analyzer import ProtocolAnalyzer
from mobile_insight.analyzer.state_machine import StateMachine
import xml.etree.ElementTree as ET

__all__ = ["LteRrcAnalyzerModified"]

class LteRrcAnalyzerModified(ProtocolAnalyzer):

    def __init__(self):
        ProtocolAnalyzer.__init__(self)

        self.add_source_callback(self.__rrc_filter)

        self.rrc_state_machine = self.create_rrc_state_machine()
        self.cell_status = None
        self.cell_history = []

    def set_source(self, source):
        ProtocolAnalyzer.set_source(self, source)

        source.enable_log("LTE_RRC_OTA_Packet")
        source.enable_log("LTE_RRC_Serv_Cell_Info")

    def create_rrc_state_machine(self):
        def to_idle(msg):
            if msg.type_id == "LTE_RRC_OTA_Packet" and "rrcConnectionRelease" in msg.data.decode():
                return True

        def to_connected(msg):
            if msg.type_id == "LTE_RRC_OTA_Packet" and "rrcConnectionSetupComplete" in msg.data.decode():
                return True

        state_machine = {
            "IDLE": {"CONNECTED": to_connected},
            "CONNECTED": {"IDLE": to_idle}
        }

        def init_state(msg):
            if msg.type_id == "LTE_RRC_OTA_Packet" and "rrcConnectionSetupComplete" in msg.data.decode():
                return "CONNECTED"
            return "IDLE"

        return StateMachine(state_machine, init_state)

    def __rrc_filter(self, msg):
        if msg.type_id == "LTE_RRC_OTA_Packet":
            self.__callback_rrc_conn(msg)
            self.__callback_rrc_reconfig(msg)
            if self.rrc_state_machine.update_state(msg):
                self.log_info("RRC State: " + self.rrc_state_machine.get_current_state())

    def __callback_rrc_conn(self, msg):
        log_item = msg.data.decode()
        if "rrcConnectionSetupComplete" in log_item:
            self.cell_status = "CONNECTED"
            self.cell_history.append(("CONNECTED", msg.timestamp))
            self.broadcast_info("RRC_CONNECTION_STATUS", {"status": "CONNECTED", "timestamp": msg.timestamp})
        elif "rrcConnectionRelease" in log_item:
            self.cell_status = "IDLE"
            self.cell_history.append(("IDLE", msg.timestamp))
            self.broadcast_info("RRC_CONNECTION_STATUS", {"status": "IDLE", "timestamp": msg.timestamp})

    def __callback_rrc_reconfig(self, msg):
        log_item = msg.data.decode()
        if "rrcConnectionReconfiguration" in log_item:
            self.log_info("RRC Reconfiguration detected")
            # Here you can extract specific configuration details and broadcast them if needed

    def get_current_cell_status(self):
        return self.cell_status

    def get_cell_history(self):
        return self.cell_history
