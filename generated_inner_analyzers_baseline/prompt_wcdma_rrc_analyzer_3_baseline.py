
from mobile_insight.analyzer import ProtocolAnalyzer
from mobile_insight.analyzer.analyzer import ProfileHierarchy

class WcdmaRrcAnalyzerModified(ProtocolAnalyzer):
    def __init__(self):
        super(WcdmaRrcAnalyzerModified, self).__init__()
        self.current_cell_status = None
        self.rrc_state_machine = self.__initialize_rrc_state_machine()
        self.packet_filters = {
            "WCDMA_RRC_Serv_Cell_Info": self.__callback_serv_cell,
            "WCDMA_RRC_States": self.__callback_rrc_state,
            "WCDMA_RRC_OTA_Packet": self.__callback_sib_config
        }
        self.set_protocol("WCDMA_RRC")

    def __initialize_rrc_state_machine(self):
        # Define initial state and possible transitions
        return {
            "state": "IDLE",
            "transitions": {
                "CELL_FACH": [],
                "CELL_DCH": [],
                "URA_PCH": [],
                "CELL_PCH": [],
                "IDLE": []
            }
        }

    def __rrc_filter(self, msg):
        if msg.type_id in self.packet_filters:
            self.packet_filters[msg.type_id](msg)

    def __callback_serv_cell(self, msg):
        self.current_cell_status = msg.data
        print(f"Updated serving cell info: {self.current_cell_status}")

    def __callback_rrc_state(self, msg):
        new_state = msg.data.get("state")
        if new_state in self.rrc_state_machine["transitions"]:
            self.rrc_state_machine["state"] = new_state
            print(f"RRC state updated to: {new_state}")

    def __callback_sib_config(self, msg):
        sib_info = msg.data.get("sib_info", {})
        # Modify metrics as needed, e.g., frequency * factor
        modified_sib_info = {k: v * 2 for k, v in sib_info.items()}  # Example modification
        print(f"Modified SIB configuration: {modified_sib_info}")

    def report_current_cell_status(self):
        if self.current_cell_status:
            return f"Current Cell Status: {self.current_cell_status.dump()}"
        return "No current cell status available."

    def report_configurations(self):
        # Assuming we have a method to get configurations
        configurations = self.get_configurations()
        return f"Configurations: {configurations.dump()}"

    def create_profile_hierarchy(self):
        # Create a profile hierarchy for WCDMA RRC
        hierarchy = ProfileHierarchy()
        # Assuming we have methods to get configurations
        hierarchy.add_profile("serving_cell_config", self.get_serving_cell_config())
        hierarchy.add_profile("intra_freq", self.get_intra_freq_params())
        hierarchy.add_profile("inter_freq", self.get_inter_freq_params())
        return hierarchy

    def set_source(self, src):
        super(WcdmaRrcAnalyzerModified, self).set_source(src)
        src.add_callback(self.__rrc_filter)
