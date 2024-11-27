
#!/usr/bin/python
# Filename: modified_wcdma_rrc_analyzer.py

"""
Enhanced WCDMA RRC Analyzer for 3G RRC analysis with additional metrics

Author: Your Name
"""

import xml.etree.ElementTree as ET
from mobile_insight.analyzer.protocol_analyzer import ProtocolAnalyzer
from mobile_insight.analyzer.state_machine import StateMachine

__all__ = ["ModifiedWcdmaRrcAnalyzer"]

class ModifiedWcdmaRrcAnalyzer(ProtocolAnalyzer):

    def __init__(self):
        ProtocolAnalyzer.__init__(self)
        self.log_info("Initializing ModifiedWcdmaRrcAnalyzer...")

        self.add_source_callback(self.__rrc_filter)

        # Initialize states and configurations
        self.current_cell_status = None
        self.cell_history = []
        self.configurations = {}

        # Setup RRC state machine
        self.rrc_state_machine = self.__create_rrc_state_machine()

    def set_source(self, source):
        ProtocolAnalyzer.set_source(self, source)
        source.enable_log("WCDMA_RRC_OTA_Packet")
        source.enable_log("WCDMA_RRC_Serv_Cell_Info")
        source.enable_log("WCDMA_RRC_States")

    def __create_rrc_state_machine(self):
        def to_cell_fach(msg):
            return msg.type_id == "WCDMA_RRC_States" and msg.data["RRC State"] == "CELL_FACH"

        def to_cell_dch(msg):
            return msg.type_id == "WCDMA_RRC_States" and msg.data["RRC State"] == "CELL_DCH"

        def to_ura_pch(msg):
            return msg.type_id == "WCDMA_RRC_States" and msg.data["RRC State"] == "URA_PCH"

        def to_cell_pch(msg):
            return msg.type_id == "WCDMA_RRC_States" and msg.data["RRC State"] == "CELL_PCH"

        def to_idle(msg):
            return msg.type_id == "WCDMA_RRC_States" and msg.data["RRC State"] == "IDLE"

        def init_state(msg):
            if msg.type_id == "WCDMA_RRC_States":
                return msg.data["RRC State"]

        state_machine = {
            "CELL_FACH": {"CELL_DCH": to_cell_dch, "URA_PCH": to_ura_pch, "CELL_PCH": to_cell_pch, "IDLE": to_idle},
            "CELL_DCH": {"CELL_FACH": to_cell_fach, "URA_PCH": to_ura_pch, "CELL_PCH": to_cell_pch, "IDLE": to_idle},
            "URA_PCH": {"CELL_FACH": to_cell_fach, "CELL_DCH": to_cell_dch, "IDLE": to_idle},
            "CELL_PCH": {"CELL_FACH": to_cell_fach, "CELL_DCH": to_cell_dch, "IDLE": to_idle},
            "IDLE": {"CELL_FACH": to_cell_fach, "CELL_DCH": to_cell_dch}
        }

        return StateMachine(state_machine, init_state)

    def __rrc_filter(self, msg):
        if msg.type_id == "WCDMA_RRC_OTA_Packet":
            self.__process_rrc_ota_packet(msg)
        elif msg.type_id == "WCDMA_RRC_Serv_Cell_Info":
            self.__process_serv_cell_info(msg)
        elif msg.type_id == "WCDMA_RRC_States":
            self.__process_rrc_states(msg)

    def __process_rrc_ota_packet(self, msg):
        log_item = msg.data.decode()
        # Process OTA packet for additional metrics
        self.log_info(f"Processing WCDMA RRC OTA Packet: {log_item}")

    def __process_serv_cell_info(self, msg):
        log_item = msg.data.decode()
        self.current_cell_status = log_item
        self.cell_history.append(log_item)
        self.log_info(f"Updated Serving Cell Info: {log_item}")

    def __process_rrc_states(self, msg):
        log_item = msg.data.decode()
        if self.rrc_state_machine.update_state(msg):
            self.log_info(f"RRC State changed to: {self.rrc_state_machine.get_current_state()}")

    def get_cell_ids(self):
        return [cell['Cell ID'] for cell in self.cell_history if 'Cell ID' in cell]

    def get_current_cell_status(self):
        return self.current_cell_status

    def get_configurations(self):
        return self.configurations
