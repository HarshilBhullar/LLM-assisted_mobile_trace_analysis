
from mobile_insight.analyzer import ProtocolAnalyzer

class LteRrcAnalyzerModified(ProtocolAnalyzer):
    def __init__(self):
        super(LteRrcAnalyzerModified, self).__init__()
        self.current_cell_status = None
        self.cell_history = []
        self.configurations = {}

        # Register source callbacks
        self.add_source_callback("LTE_RRC_OTA_Packet", self.__rrc_filter)
        self.add_source_callback("LTE_RRC_Serv_Cell_Info", self.__callback_sib_config)
        self.add_source_callback("LTE_RRC_CDRX_Events_Info", self.__callback_rrc_reconfig)
        
    def set_source(self, source):
        source.enable_log("LTE_RRC_OTA_Packet")
        source.enable_log("LTE_RRC_Serv_Cell_Info")
        source.enable_log("LTE_RRC_CDRX_Events_Info")
        super(LteRrcAnalyzerModified, self).set_source(source)

    def create_state_machine(self):
        # Example state machine setup for LTE RRC states
        self.state_machine = {
            "RRC_IDLE": self.__state_rrc_idle,
            "RRC_CRX": self.__state_rrc_crx,
        }
        self.current_state = "RRC_IDLE"

    def __state_rrc_idle(self, msg):
        # Logic to handle RRC_IDLE state
        if msg.type_id == "LTE_RRC_Connection_Request":
            self.current_state = "RRC_CRX"

    def __state_rrc_crx(self, msg):
        # Logic to handle RRC_CRX state
        if msg.type_id == "LTE_RRC_Connection_Release":
            self.current_state = "RRC_IDLE"

    def __rrc_filter(self, msg):
        # Process incoming RRC messages
        if msg.type_id in self.state_machine:
            self.state_machine[msg.type_id](msg)
        self.broadcast_info("Processed RRC message: " + msg.type_id)

    def __callback_sib_config(self, msg):
        # Extract configurations from System Information Blocks (SIBs)
        if msg.type_id == "LTE_RRC_Serv_Cell_Info":
            self.configurations['radio_thresholds'] = msg.get('radio_thresholds', {})
            self.configurations['preferences'] = msg.get('preferences', {})
            self.broadcast_info("Updated SIB configurations")

    def __callback_rrc_reconfig(self, msg):
        # Process RRC Reconfiguration messages
        if msg.type_id == "LTE_RRC_Reconfiguration":
            self.current_cell_status = msg.get('cell_status', {})
            self.cell_history.append(self.current_cell_status)
            self.broadcast_info("Processed RRC Reconfiguration")
