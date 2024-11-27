
from mobile_insight.analyzer.analyzer import ProtocolAnalyzer

class UmtsNasAnalyzerModified(ProtocolAnalyzer):
    def __init__(self):
        super(UmtsNasAnalyzerModified, self).__init__()
        self.set_name("UMTS NAS Analyzer Modified")
        self.add_source_callback(self.__nas_filter)
        
        self.mm_state = "Idle"
        self.gmm_state = "Deregistered"
        self.cm_state = "Idle"
        
        self.qos_profile = {}
        self.drx_params = {}
        
    def __nas_filter(self, msg):
        if msg.type_id == "UMTS_NAS_MM_State":
            self.__callback_mm_state(msg)
        elif msg.type_id == "UMTS_NAS_GMM_State":
            self.__callback_gmm_state(msg)
        elif msg.type_id == "UMTS_NAS_OTA_Packet":
            self.__callback_nas(msg)
            
    def __callback_mm_state(self, msg):
        new_state = msg.data.get("MM State")
        if new_state != self.mm_state:
            self.mm_state = new_state
            self.log_info(f"MM State transitioned to {self.mm_state}")
        
    def __callback_mm_reg_state(self, msg):
        plmn = msg.data.get("PLMN")
        lac = msg.data.get("LAC")
        rac = msg.data.get("RAC")
        self.log_info(f"MM Registration State updated: PLMN={plmn}, LAC={lac}, RAC={rac}")
        
    def __callback_gmm_state(self, msg):
        new_state = msg.data.get("GMM State")
        if new_state != self.gmm_state:
            self.gmm_state = new_state
            self.log_info(f"GMM State transitioned to {self.gmm_state}")
        
    def __callback_nas(self, msg):
        self.__update_qos_profile(msg)
        self.__update_drx_parameters(msg)
        
    def __update_qos_profile(self, msg):
        qos = msg.data.get("QoS")
        if qos:
            self.qos_profile = qos
            self.log_info(f"QoS Profile updated: {self.qos_profile}")
        
    def __update_drx_parameters(self, msg):
        drx = msg.data.get("DRX")
        if drx:
            self.drx_params = drx
            self.log_info(f"DRX Parameters updated: {self.drx_params}")
        
    def create_profile_hierarchy(self):
        profile = {
            "MM State": self.mm_state,
            "GMM State": self.gmm_state,
            "QoS Profile": self.qos_profile,
            "DRX Parameters": self.drx_params
        }
        return profile
        
    def set_source(self, source):
        super(UmtsNasAnalyzerModified, self).set_source(source)
        source.enable_log("UMTS_NAS_OTA_Packet")
        source.enable_log("UMTS_NAS_GMM_State")
        source.enable_log("UMTS_NAS_MM_State")
