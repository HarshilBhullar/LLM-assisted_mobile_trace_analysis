
import xml.etree.ElementTree as ET
from mobile_insight.analyzer.analyzer import Analyzer

class ModifiedMmAnalyzer(Analyzer):
    def __init__(self):
        super().__init__()
        self.umts_spans = []
        self.lte_spans = []
        self.lte_plmn_search_count = 0
        self.current_spans = {}

    def set_source(self, source):
        super().set_source(source)
        source.enable_log("UMTS_NAS_GMM_State")
        source.enable_log("LTE_NAS_EMM_State")
        source.enable_log("LTE_RRC_OTA_Packet")
        source.enable_log("UMTS_NAS_OTA_Packet")

    def get_umts_service_spans(self):
        return self.umts_spans

    def get_lte_service_spans(self):
        return self.lte_spans

    def get_lte_plmn_search_count(self):
        return self.lte_plmn_search_count

    def callback_umts_nas_gmm_state(self, msg):
        state = self._parse_state(msg, "UMTS_NAS_GMM_State")
        self._process_state_change(state, "UMTS")

    def callback_lte_nas_emm_state(self, msg):
        state = self._parse_state(msg, "LTE_NAS_EMM_State")
        self._process_state_change(state, "LTE")

    def callback_lte_rrc_ota_packet(self, msg):
        if self._is_plmn_search(msg):
            self.lte_plmn_search_count += 1

    def _parse_state(self, msg, log_type):
        try:
            root = ET.fromstring(msg.data.decode('utf-8'))
            state_element = root.find(log_type)
            if state_element is not None:
                return state_element.text
        except ET.ParseError:
            self.log_warning("Failed to parse XML message.")
        return None

    def _process_state_change(self, state, network_type):
        timestamp = self.get_cur_msg_timestamp()
        if state == "NORMAL_SERVICE":
            self._start_span(network_type, timestamp)
        elif state in ["PLMN_SEARCH", "ATTACH", "UPDATE"]:
            self._end_span(network_type, timestamp)

    def _start_span(self, network_type, timestamp):
        if network_type not in self.current_spans:
            self.current_spans[network_type] = timestamp

    def _end_span(self, network_type, timestamp):
        if network_type in self.current_spans:
            start_time = self.current_spans.pop(network_type)
            span = (start_time, timestamp)
            if network_type == "UMTS":
                self.umts_spans.append(span)
            elif network_type == "LTE":
                self.lte_spans.append(span)

    def _is_plmn_search(self, msg):
        try:
            root = ET.fromstring(msg.data.decode('utf-8'))
            procedure_element = root.find("Procedure")
            if procedure_element is not None and "PLMN_SEARCH" in procedure_element.text:
                return True
        except ET.ParseError:
            self.log_warning("Failed to parse XML message.")
        return False

    def on_log_packet(self, msg):
        if msg.type_id == "UMTS_NAS_GMM_State":
            self.callback_umts_nas_gmm_state(msg)
        elif msg.type_id == "LTE_NAS_EMM_State":
            self.callback_lte_nas_emm_state(msg)
        elif msg.type_id == "LTE_RRC_OTA_Packet":
            self.callback_lte_rrc_ota_packet(msg)
