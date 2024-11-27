
import datetime
from mobile_insight.analyzer.analyzer import Analyzer

class Span:
    def __init__(self, start_time=None, end_time=None, span_type=""):
        self.start_time = start_time
        self.end_time = end_time
        self.span_type = span_type

    def start(self, start_time):
        self.start_time = start_time

    def end(self, end_time):
        self.end_time = end_time

    def is_active(self):
        return self.start_time is not None and self.end_time is None

    def get_duration(self):
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

class ModifiedMmAnalyzer(Analyzer):
    def __init__(self):
        super().__init__()
        self.umts_normal_service_spans = []
        self.umts_plmn_search_spans = []
        self.lte_attach_spans = []

    def set_source(self, source):
        super().set_source(source)
        source.enable_log("LTE_NAS_EMM_State")
        source.enable_log("UMTS_NAS_GMM_State")
        source.enable_log("WCDMA_RRC_OTA")
        source.enable_log("LTE_RRC_OTA")

    def __filter(self, msg):
        if "LTE_NAS_EMM_State" in msg.type_id:
            self.__callback_lte_nas_emm(msg)
        elif "UMTS_NAS_GMM_State" in msg.type_id:
            self.__callback_umts_nas_gmm(msg)
        elif "WCDMA_RRC_OTA" in msg.type_id:
            self.__callback_wcdma_rrc_ota(msg)
        elif "LTE_RRC_OTA" in msg.type_id:
            self.__callback_lte_rrc_ota(msg)

    def __callback_umts_nas_gmm(self, msg):
        # Implement UMTS NAS GMM event handling
        timestamp = msg.timestamp
        for event in msg.data.get("events", []):
            if event.get("type") == "PLMN_SEARCH":
                if not self.umts_plmn_search_spans or not self.umts_plmn_search_spans[-1].is_active():
                    span = Span(start_time=timestamp, span_type="PLMN_SEARCH")
                    self.umts_plmn_search_spans.append(span)
            elif event.get("type") == "NORMAL_SERVICE":
                if self.umts_plmn_search_spans and self.umts_plmn_search_spans[-1].is_active():
                    self.umts_plmn_search_spans[-1].end(timestamp)
                span = Span(start_time=timestamp, span_type="NORMAL_SERVICE")
                self.umts_normal_service_spans.append(span)

    def __callback_wcdma_rrc_ota(self, msg):
        # Implement WCDMA RRC OTA handling
        pass

    def __callback_lte_rrc_ota(self, msg):
        # Implement LTE RRC OTA handling
        pass

    def __callback_lte_nas_emm(self, msg):
        # Implement LTE NAS EMM State handling
        timestamp = msg.timestamp
        for event in msg.data.get("events", []):
            if event.get("type") == "ATTACH":
                span = Span(start_time=timestamp, span_type="ATTACH")
                self.lte_attach_spans.append(span)

    def get_umts_normal_service_log(self):
        return [span.get_duration() for span in self.umts_normal_service_spans if span.get_duration()]

    def get_umts_plmn_search_log(self):
        return [span.get_duration() for span in self.umts_plmn_search_spans if span.get_duration()]

    def get_lte_attach_log(self):
        return [span.get_duration() for span in self.lte_attach_spans if span.get_duration()]
