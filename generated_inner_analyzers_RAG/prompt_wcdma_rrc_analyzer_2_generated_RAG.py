
#!/usr/bin/python
# Filename: modified_wcdma_rrc_analyzer.py

"""
Modified WCDMA RRC Analyzer with adjusted metrics.
"""

from mobile_insight.analyzer.analyzer import ProtocolAnalyzer
from mobile_insight.analyzer.state_machine import StateMachine
import xml.etree.ElementTree as ET

__all__ = ["ModifiedWcdmaRrcAnalyzer"]

class ModifiedWcdmaRrcAnalyzer(ProtocolAnalyzer):
    """
    A modified protocol analyzer for WCDMA RRC.
    """

    def __init__(self):
        self.log_info("Initializing ModifiedWcdmaRrcAnalyzer..")

        ProtocolAnalyzer.__init__(self)
        self.add_source_callback(self.__rrc_filter)

        self.rrc_state_machine = self.create_state_machine()
        self.cell_configurations = {}
        self.current_cell = None

    def create_state_machine(self):
        """
        Declare a WCDMA RRC state machine

        Returns: a StateMachine
        """

        def to_cell_fach(msg):
            return msg.type_id == "WCDMA_RRC_State" and msg.data["RRC State"] == "CELL_FACH"

        def to_cell_dch(msg):
            return msg.type_id == "WCDMA_RRC_State" and msg.data["RRC State"] == "CELL_DCH"

        def to_ura_pch(msg):
            return msg.type_id == "WCDMA_RRC_State" and msg.data["RRC State"] == "URA_PCH"

        def to_cell_pch(msg):
            return msg.type_id == "WCDMA_RRC_State" and msg.data["RRC State"] == "CELL_PCH"

        def to_idle(msg):
            return msg.type_id == "WCDMA_RRC_State" and msg.data["RRC State"] == "IDLE"

        state_machine = {
            "IDLE": {"CELL_FACH": to_cell_fach, "CELL_DCH": to_cell_dch},
            "CELL_FACH": {"CELL_DCH": to_cell_dch, "IDLE": to_idle},
            "CELL_DCH": {"CELL_FACH": to_cell_fach, "URA_PCH": to_ura_pch, "CELL_PCH": to_cell_pch, "IDLE": to_idle},
            "URA_PCH": {"CELL_FACH": to_cell_fach, "IDLE": to_idle},
            "CELL_PCH": {"CELL_FACH": to_cell_fach, "IDLE": to_idle},
        }

        return StateMachine(state_machine, to_idle)

    def set_source(self, source):
        """
        Set the trace source. Enable the WCDMA RRC messages.

        :param source: the trace source.
        """
        ProtocolAnalyzer.set_source(self, source)
        source.enable_log("WCDMA_RRC_OTA_Packet")
        source.enable_log("WCDMA_RRC_State")
        source.enable_log("WCDMA_RRC_Serv_Cell_Info")

    def __rrc_filter(self, msg):
        """
        Filter all RRC-related packets and process them.

        :param msg: the event (message) from the trace collector.
        """
        if msg.type_id == "WCDMA_RRC_State":
            self.__callback_rrc_state(msg)
        elif msg.type_id == "WCDMA_RRC_Serv_Cell_Info":
            self.__callback_serv_cell(msg)
        elif msg.type_id == "WCDMA_RRC_OTA_Packet":
            self.__callback_sib_config(msg)

    def __callback_rrc_state(self, msg):
        """
        Handle RRC state messages.

        :param msg: the RRC state message.
        """
        if self.rrc_state_machine.update_state(msg):
            self.log_info("RRC State: " + self.rrc_state_machine.get_current_state())
            self.broadcast_info("RRC_STATE", {"state": self.rrc_state_machine.get_current_state(), "additional_info": "Modified Analyzer"})

    def __callback_serv_cell(self, msg):
        """
        Handle serving cell information messages.

        :param msg: the serving cell information message.
        """
        self.current_cell = msg.data["Cell ID"]
        self.cell_configurations[self.current_cell] = {
            "frequency": msg.data["UARFCN DL"],
            "cell_id": msg.data["Cell ID"]
        }
        self.log_info(f"Serving Cell Info: {self.cell_configurations[self.current_cell]}")

    def __callback_sib_config(self, msg):
        """
        Handle SIB configuration messages.

        :param msg: the SIB configuration message.
        """
        log_item = msg.data.decode()
        log_xml = ET.XML(log_item)
        for sib in log_xml.iter("field"):
            if sib.get("name") == "rrc.SystemInformationBlockType1":
                self.cell_configurations[self.current_cell]["SIB1"] = sib.get("value")
                self.log_info(f"SIB1 Config: {sib.get('value')}")

    def create_profile_hierarchy(self):
        """
        Return a WCDMA RRC ProfileHierarchy (configurations).

        :returns: ProfileHierarchy for WCDMA RRC
        """
        profile_hierarchy = ProfileHierarchy('WcdmaRrcProfile')
        root = profile_hierarchy.get_root()
        idle = root.add('idle', False)
        active = root.add('active', False)

        # Add relevant fields to profiles
        idle.add('frequency', False)
        idle.add('cell_id', False)

        active.add('RRC_state', False)
        active.add('SIB1', False)

        return profile_hierarchy

    def get_current_cell_config(self):
        """
        Get the current cell configuration.

        :returns: The current cell's configuration.
        """
        return self.cell_configurations.get(self.current_cell, None)

    def get_all_cells(self):
        """
        Get a list of all cells associated with the device.

        :returns: A list of all cell configurations.
        """
        return list(self.cell_configurations.values())
