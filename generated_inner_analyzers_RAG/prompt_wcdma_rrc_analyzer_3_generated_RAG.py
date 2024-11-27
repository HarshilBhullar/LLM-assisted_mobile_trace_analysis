
#!/usr/bin/python
# Filename: wcdma_rrc_analyzer_modified.py

from mobile_insight.analyzer.analyzer import *
from mobile_insight.analyzer.protocol_analyzer import *

__all__ = ["WcdmaRrcAnalyzerModified"]

class WcdmaRrcAnalyzerModified(ProtocolAnalyzer):
    def __init__(self):
        ProtocolAnalyzer.__init__(self)

        self.add_source_callback(self.__rrc_filter)

        self.__status = WcdmaRrcStatus()  # Current cell status
        self.__history = {}  # Cell history: timestamp -> WcdmaRrcStatus()
        self.__config = {}  # (cell_id, freq) -> WcdmaRrcConfig()

        self.__rrc_state_machine = WcdmaRrcStateMachine()

    def set_source(self, source):
        ProtocolAnalyzer.set_source(self, source)
        source.enable_log("WCDMA_RRC_Serv_Cell_Info")
        source.enable_log("WCDMA_RRC_States")
        source.enable_log("WCDMA_RRC_OTA_Packet")

    def __rrc_filter(self, msg):
        log_item = msg.data.decode()
        if msg.type_id == "WCDMA_RRC_Serv_Cell_Info":
            self.__callback_serv_cell(log_item)
        elif msg.type_id == "WCDMA_RRC_States":
            self.__callback_rrc_state(log_item)
        elif msg.type_id == "WCDMA_RRC_OTA_Packet":
            self.__callback_sib_config(log_item)

    def __callback_serv_cell(self, log_item):
        freq = int(log_item["Freq"])
        cid = int(log_item["Cell ID"])
        timestamp = log_item["timestamp"]
        self.__status.freq = freq
        self.__status.id = cid
        self.__history[timestamp] = self.__status

    def __callback_rrc_state(self, log_item):
        new_state = log_item["RRC State"]
        self.__rrc_state_machine.update_state(new_state)

    def __callback_sib_config(self, log_item):
        # Process SIB configurations and modify metrics
        for field in log_item["fields"]:
            if field["name"] == "intraFreqNeighCellList":
                freq = int(field["value"]) * 2  # Example modification
                # Update configurations
                self.__config[(self.__status.id, freq)] = WcdmaRrcConfig()

    def create_profile_hierarchy(self):
        # Create a profile hierarchy for WCDMA RRC
        return ProfileHierarchy()

    def get_cur_cell_status(self):
        return self.__status

    def get_cell_config(self, cell):
        if cell in self.__config:
            return self.__config[cell]
        return None

    def get_mobility_history(self):
        return self.__history

class WcdmaRrcStatus:
    def __init__(self):
        self.id = None
        self.freq = None

    def dump(self):
        return f"WcdmaRrcStatus: id={self.id}, freq={self.freq}"

class WcdmaRrcConfig:
    def __init__(self):
        self.active = WcdmaRrcActive()

    def dump(self):
        return f"WcdmaRrcConfig:\n{self.active.dump()}"

class WcdmaRrcActive:
    def __init__(self):
        self.params = {}

    def dump(self):
        return "WcdmaRrcActive: " + str(self.params)

class WcdmaRrcStateMachine:
    def __init__(self):
        self.current_state = "IDLE"

    def update_state(self, new_state):
        self.current_state = new_state

class ProfileHierarchy:
    def __init__(self):
        pass
