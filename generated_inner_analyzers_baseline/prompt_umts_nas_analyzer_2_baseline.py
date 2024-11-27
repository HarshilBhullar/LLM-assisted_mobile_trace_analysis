
from mobileinsight.analyzer.analyzer import ProtocolAnalyzer

class UmtsNasAnalyzerModified(ProtocolAnalyzer):
    
    def __init__(self):
        super(UmtsNasAnalyzerModified, self).__init__()
        self.set_protocol("UMTS_NAS")
        self.__mm_state = 'MM_IDLE'
        self.__gmm_state = 'GMM_DEREGISTERED'
        self.__cm_state = 'CM_IDLE'
        
        self.add_source_callback(self.__nas_filter)
    
    def __nas_filter(self, msg):
        if msg.type_id == "UMTS_NAS_MM_State":
            self.__process_mm_state(msg)
        elif msg.type_id == "UMTS_NAS_GMM_State":
            self.__process_gmm_state(msg)
        elif msg.type_id == "UMTS_NAS_OTA_Packet":
            self.__process_cm_state(msg)
    
    def __process_mm_state(self, msg):
        if "MM_IDLE" in msg.data:
            self.__mm_state = 'MM_IDLE'
        elif "MM_WAIT_FOR_NETWORK_COMMAND" in msg.data:
            self.__mm_state = 'MM_WAIT_FOR_NETWORK_COMMAND'
        elif "MM_CONNECTION_ACTIVE" in msg.data:
            self.__mm_state = 'MM_CONNECTION_ACTIVE'
        
        self.__broadcast_state("MM", self.__mm_state)
    
    def __process_gmm_state(self, msg):
        if "GMM_REGISTERED" in msg.data:
            self.__gmm_state = 'GMM_REGISTERED'
        elif "GMM_DEREGISTERED" in msg.data:
            self.__gmm_state = 'GMM_DEREGISTERED'
        
        self.__broadcast_state("GMM", self.__gmm_state)
    
    def __process_cm_state(self, msg):
        if "CM_SERVICE_REQUEST" in msg.data:
            self.__cm_state = 'CM_SERVICE_REQUEST'
        elif "CM_SETUP" in msg.data:
            self.__cm_state = 'CM_SETUP'
        elif "CM_CALL_PROCEEDING" in msg.data:
            self.__cm_state = 'CM_CALL_PROCEEDING'
        
        self.__broadcast_state("CM", self.__cm_state)
    
    def __broadcast_state(self, layer, state):
        print(f"Updated {layer} state: {state}")
