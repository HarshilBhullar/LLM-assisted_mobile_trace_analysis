
#!/usr/bin/python
# Filename: modified_mm_analyzer.py
"""
A modified MM analyzer to track and analyze MM state changes with enhancements

"""

from mobile_insight.analyzer.analyzer import *
from datetime import datetime

__all__ = ["ModifiedMmAnalyzer"]

class Span:
    def __init__(self, start_time, end_time=None):
        self.start_time = start_time
        self.end_time = end_time

    def end(self, end_time):
        self.end_time = end_time

class ModifiedMmAnalyzer(Analyzer):

    def __init__(self):
        Analyzer.__init__(self)

        self.add_source_callback(self.__filter)

        # Initialize span lists
        self.lte_normal_service_spans = []
        self.lte_attach_spans = []
        self.umts_normal_service_spans = []
        self.umts_plmn_search_spans = []

    def set_source(self, source):
        """
        Set the trace source. Enable the cellular signaling messages

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)

        # Enable specific logs
        source.enable_log("LTE_NAS_EMM_State")
        source.enable_log("LTE_NAS_ESM_State")
        source.enable_log("LTE_RRC_OTA_Packet")
        source.enable_log("UMTS_NAS_GMM_State")
        source.enable_log("WCDMA_RRC_OTA_Packet")

    def __filter(self, msg):
        if msg.type_id == "LTE_NAS_EMM_State":
            self.__callback_lte_nas_emm(msg)
        elif msg.type_id == "UMTS_NAS_GMM_State":
            self.__callback_umts_nas_gmm(msg)
        elif msg.type_id == "WCDMA_RRC_OTA_Packet":
            self.__callback_wcdma_rrc_ota(msg)
        elif msg.type_id == "LTE_RRC_OTA_Packet":
            self.__callback_lte_rrc_ota(msg)

    def __callback_lte_nas_emm(self, msg):
        log_item = msg.data.decode()
        emm_state = log_item['emm_state']

        if emm_state == "EMM-REGISTERED":
            self.start_span(self.lte_normal_service_spans, log_item['timestamp'])
        elif emm_state == "EMM-DEREGISTERED":
            self.end_span(self.lte_normal_service_spans, log_item['timestamp'])

    def __callback_umts_nas_gmm(self, msg):
        log_item = msg.data.decode()
        gmm_state = log_item['gmm_state']

        if gmm_state == "GMM-REGISTERED":
            self.start_span(self.umts_normal_service_spans, log_item['timestamp'])
        elif gmm_state == "GMM-DEREGISTERED":
            self.end_span(self.umts_normal_service_spans, log_item['timestamp'])

    def __callback_wcdma_rrc_ota(self, msg):
        log_item = msg.data.decode()
        # Process WCDMA RRC OTA messages for cell info
        self.log_info("WCDMA RRC OTA message: " + str(log_item))

    def __callback_lte_rrc_ota(self, msg):
        log_item = msg.data.decode()
        # Process LTE RRC OTA messages for configuration and cell reselection
        self.log_info("LTE RRC OTA message: " + str(log_item))

    def start_span(self, span_list, timestamp):
        span_list.append(Span(timestamp))

    def end_span(self, span_list, timestamp):
        if span_list and span_list[-1].end_time is None:
            span_list[-1].end(timestamp)

    def get_lte_normal_service_log(self):
        return [(span.start_time, span.end_time) for span in self.lte_normal_service_spans]

    def get_umts_normal_service_log(self):
        return [(span.start_time, span.end_time) for span in self.umts_normal_service_spans]

    def get_umts_plmn_search_log(self):
        return [(span.start_time, span.end_time) for span in self.umts_plmn_search_spans]

    # Additional methods for retrieving other logs can be added here

