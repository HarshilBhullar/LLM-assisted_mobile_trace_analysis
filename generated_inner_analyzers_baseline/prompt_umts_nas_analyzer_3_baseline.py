
from mobile_insight.analyzer.analyzer import ProtocolAnalyzer

class UmtsNasAnalyzerModified(ProtocolAnalyzer):
    def __init__(self):
        super(UmtsNasAnalyzerModified, self).__init__()
        self.log_info("UmtsNasAnalyzerModified is initialized")
        self.__nas_filter()

    def __nas_filter(self):
        self.add_source_callback(self.__callback_mm_state, "UMTS_NAS_MM_State")
        self.add_source_callback(self.__callback_mm_reg_state, "UMTS_NAS_MM_REG_State")
        self.add_source_callback(self.__callback_gmm_state, "UMTS_NAS_GMM_State")
        self.add_source_callback(self.__callback_nas, "UMTS_NAS_OTA_Packet")

    def create_mm_state_machine(self):
        # Example state machine creation logic
        pass

    def create_gmm_state_machine(self):
        # Example state machine creation logic
        pass

    def create_cm_state_machine(self):
        # Example state machine creation logic
        pass

    def create_profile_hierarchy(self):
        # Example profile hierarchy creation
        return "ProfileHierarchy for UMTS NAS"

    def __callback_mm_state(self, msg):
        # Example message processing and state update
        mm_status = "MM Status"  # Extract MM status from msg
        self.broadcast_info({
            "status": mm_status,
            "additional_info": "Modified Analyzer"
        })

    def __callback_mm_reg_state(self, msg):
        # Example message processing and state update
        mm_reg_status = "MM REG Status"  # Extract MM REG status from msg
        self.broadcast_info({
            "status": mm_reg_status,
            "additional_info": "Modified Analyzer"
        })

    def __callback_gmm_state(self, msg):
        # Example message processing and state update
        gmm_status = "GMM Status"  # Extract GMM status from msg
        self.broadcast_info({
            "status": gmm_status,
            "additional_info": "Modified Analyzer"
        })

    def __callback_nas(self, msg):
        # Example message processing and state update
        nas_status = "NAS Status"  # Extract NAS status from msg
        self.broadcast_info({
            "status": nas_status,
            "additional_info": "Modified Analyzer"
        })

    def set_source(self, source):
        super(UmtsNasAnalyzerModified, self).set_source(source)
        source.enable_log("UMTS_NAS_OTA_Packet")
        source.enable_log("UMTS_NAS_GMM_State")
        source.enable_log("UMTS_NAS_MM_State")
        source.enable_log("UMTS_NAS_MM_REG_State")
