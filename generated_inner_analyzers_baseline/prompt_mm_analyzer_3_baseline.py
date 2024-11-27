
import re
from mobile_insight.analyzer.analyzer import Analyzer

class MmAnalyzerModified(Analyzer):
    def __init__(self):
        super(MmAnalyzerModified, self).__init__()
        self.umts_spans = {
            "normal_service": [],
            "plmn_search": [],
            "attach": [],
            "location_update": [],
            "routing_area_update": []
        }
        self.lte_spans = {
            "normal_service": [],
            "plmn_search": [],
            "attach": [],
            "tau": []
        }
        self.lte_configurations = {
            "tau_qos_info": None,
            "cell_reselection_to_umts": None,
            "drx_configuration": None,
            "tdd_configuration": None
        }

    def set_source(self, source):
        self.source = source
        source.enable_log_all()
        source.add_callback("NAS_GMM_State", self.__nas_gmm_state_handler)
        source.add_callback("UMTS_NAS_OTA_Packet", self.__umts_nas_ota_handler)
        source.add_callback("NAS_EMM_State", self.__nas_emm_state_handler)
        source.add_callback("LTE_NAS_OTA_Packet", self.__lte_nas_ota_handler)
        source.add_callback("LTE_RRC_OTA_Packet", self.__lte_rrc_ota_handler)
        source.add_callback("WCDMA_RRC_OTA_Packet", self.__wcdma_rrc_ota_handler)

    def __filter(self, msg):
        try:
            decoded_msg = msg.decode()
            if "event_type" in decoded_msg:
                event_type = decoded_msg["event_type"]
                if hasattr(self, f"__{event_type}_handler"):
                    handler = getattr(self, f"__{event_type}_handler")
                    handler(decoded_msg)
        except Exception as e:
            self.log_error(f"Error processing message: {str(e)}")

    def __nas_gmm_state_handler(self, msg):
        # Handle UMTS NAS GMM State
        pass

    def __umts_nas_ota_handler(self, msg):
        # Handle UMTS NAS OTA Packet
        pass

    def __nas_emm_state_handler(self, msg):
        # Handle LTE NAS EMM State
        pass

    def __lte_nas_ota_handler(self, msg):
        # Handle LTE NAS OTA Packet
        pass

    def __lte_rrc_ota_handler(self, msg):
        # Handle LTE RRC OTA Packet
        pass

    def __wcdma_rrc_ota_handler(self, msg):
        # Handle WCDMA RRC OTA Packet
        pass

    def start_span(self, category, network_type, start_time):
        if network_type == "UMTS":
            if category in self.umts_spans:
                self.umts_spans[category].append({"start": start_time, "end": None})
        elif network_type == "LTE":
            if category in self.lte_spans:
                self.lte_spans[category].append({"start": start_time, "end": None})

    def end_span(self, category, network_type, end_time):
        if network_type == "UMTS":
            if category in self.umts_spans and self.umts_spans[category]:
                self.umts_spans[category][-1]["end"] = end_time
        elif network_type == "LTE":
            if category in self.lte_spans and self.lte_spans[category]:
                self.lte_spans[category][-1]["end"] = end_time

    def get_logs(self):
        return {
            "UMTS": self.umts_spans,
            "LTE": self.lte_spans,
            "LTE Configurations": self.lte_configurations
        }
