
#!/usr/bin/python
# Filename: modified_mm_analyzer.py

from mobile_insight.analyzer.analyzer import Analyzer
from datetime import datetime

class ModifiedMmAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__filter)

        # Span lists for different network activities
        self.umts_normal_service_spans = []
        self.umts_plmn_search_spans = []
        self.lte_attach_spans = []
        self.lte_normal_service_spans = []

        # Current states and spans
        self.current_umts_service_span = None
        self.current_umts_plmn_span = None
        self.current_lte_attach_span = None
        self.current_lte_service_span = None

    def set_source(self, source):
        """
        Set the trace source. Enable the specific logs.

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)
        source.enable_log("LTE_NAS_EMM_State")
        source.enable_log("UMTS_NAS_GMM_State")
        source.enable_log("LTE_RRC_OTA_Packet")
        source.enable_log("UMTS_RRC_OTA_Packet")

    def __filter(self, msg):
        """
        Filter messages and invoke specific handling methods

        :param msg: the event (message) from the trace collector.
        """
        if msg.type_id == "UMTS_NAS_GMM_State":
            self.__callback_umts_nas_gmm(msg)
        elif msg.type_id == "UMTS_RRC_OTA_Packet":
            self.__callback_wcdma_rrc_ota(msg)
        elif msg.type_id == "LTE_RRC_OTA_Packet":
            self.__callback_lte_rrc_ota(msg)

    def __callback_umts_nas_gmm(self, msg):
        """
        Handle UMTS NAS GMM events to track normal service and PLMN search spans

        :param msg: UMTS NAS GMM message
        """
        data = msg.data.decode()
        if "Service Request" in data:
            self.start_span("UMTS_NORMAL_SERVICE")
        elif "Service Release" in data:
            self.end_span("UMTS_NORMAL_SERVICE")
        elif "PLMN Search" in data:
            self.start_span("UMTS_PLMN_SEARCH")
        elif "PLMN Search End" in data:
            self.end_span("UMTS_PLMN_SEARCH")

    def __callback_wcdma_rrc_ota(self, msg):
        """
        Process WCDMA RRC OTA messages to extract and log cell information

        :param msg: WCDMA RRC OTA message
        """
        pass  # Implement specific logic if needed

    def __callback_lte_rrc_ota(self, msg):
        """
        Handle LTE RRC OTA messages to track configuration changes and cell reselection information

        :param msg: LTE RRC OTA message
        """
        data = msg.data.decode()
        if "Attach Request" in data:
            self.start_span("LTE_ATTACH")
        elif "Attach Complete" in data:
            self.end_span("LTE_ATTACH")
        elif "Service Request" in data:
            self.start_span("LTE_NORMAL_SERVICE")
        elif "Service Release" in data:
            self.end_span("LTE_NORMAL_SERVICE")

    def start_span(self, span_type):
        """
        Start a new span of the specified type

        :param span_type: the type of span to start
        """
        current_time = datetime.now()
        if span_type == "UMTS_NORMAL_SERVICE":
            self.current_umts_service_span = current_time
        elif span_type == "UMTS_PLMN_SEARCH":
            self.current_umts_plmn_span = current_time
        elif span_type == "LTE_ATTACH":
            self.current_lte_attach_span = current_time
        elif span_type == "LTE_NORMAL_SERVICE":
            self.current_lte_service_span = current_time

    def end_span(self, span_type):
        """
        End the current span of the specified type

        :param span_type: the type of span to end
        """
        current_time = datetime.now()
        if span_type == "UMTS_NORMAL_SERVICE" and self.current_umts_service_span:
            self.umts_normal_service_spans.append(
                (self.current_umts_service_span, current_time))
            self.current_umts_service_span = None
        elif span_type == "UMTS_PLMN_SEARCH" and self.current_umts_plmn_span:
            self.umts_plmn_search_spans.append(
                (self.current_umts_plmn_span, current_time))
            self.current_umts_plmn_span = None
        elif span_type == "LTE_ATTACH" and self.current_lte_attach_span:
            self.lte_attach_spans.append(
                (self.current_lte_attach_span, current_time))
            self.current_lte_attach_span = None
        elif span_type == "LTE_NORMAL_SERVICE" and self.current_lte_service_span:
            self.lte_normal_service_spans.append(
                (self.current_lte_service_span, current_time))
            self.current_lte_service_span = None

    def get_umts_normal_service_log(self):
        return self.umts_normal_service_spans

    def get_umts_plmn_search_log(self):
        return self.umts_plmn_search_spans

    def get_lte_attach_log(self):
        return self.lte_attach_spans

    def get_lte_normal_service_log(self):
        return self.lte_normal_service_spans
