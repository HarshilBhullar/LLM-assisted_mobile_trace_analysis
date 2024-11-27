
#!/usr/bin/python
# Filename: modified_mm_analyzer.py
"""
Modified MM Analyzer for enhanced state change tracking and analysis

Author: Your Name
"""

from mobile_insight.analyzer.analyzer import Analyzer
import xml.etree.ElementTree as ET
from datetime import datetime

__all__ = ["ModifiedMmAnalyzer"]

class ModifiedMmAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)

        # Internal logs and metrics
        self.umts_service_spans = []
        self.lte_service_spans = []
        self.umts_plmn_searches = 0
        self.lte_plmn_searches = 0
        self.lte_rrc_reconfigs = 0
        self.current_umts_span = None
        self.current_lte_span = None

    def set_source(self, source):
        """
        Set the trace source and enable necessary logs

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)
        source.enable_log("UMTS_NAS_GMM_State")
        source.enable_log("LTE_NAS_EMM_State")
        source.enable_log("LTE_RRC_OTA_Packet")
        source.enable_log("UMTS_NAS_OTA_Packet")

    def __msg_callback(self, msg):
        """
        Callback for processing network events

        :param msg: the event (message) from the trace collector.
        """
        if msg.type_id == "UMTS_NAS_GMM_State":
            self.__process_umts_gmm_state(msg)
        elif msg.type_id == "LTE_NAS_EMM_State":
            self.__process_lte_emm_state(msg)
        elif msg.type_id == "LTE_RRC_OTA_Packet":
            self.__process_lte_rrc_ota_packet(msg)
        elif msg.type_id == "UMTS_NAS_OTA_Packet":
            self.__process_umts_nas_ota_packet(msg)

    def __process_umts_gmm_state(self, msg):
        """
        Process UMTS GMM State messages for service span logging

        :param msg: the UMTS GMM State message
        """
        state = msg.data.get("GMM State", "")
        timestamp = msg.timestamp

        if state == "GMM_REGISTERED":
            if not self.current_umts_span:
                self.current_umts_span = [timestamp, None]
        else:
            if self.current_umts_span:
                self.current_umts_span[1] = timestamp
                self.umts_service_spans.append(tuple(self.current_umts_span))
                self.current_umts_span = None

    def __process_lte_emm_state(self, msg):
        """
        Process LTE EMM State messages for service span logging

        :param msg: the LTE EMM State message
        """
        state = msg.data.get("EMM State", "")
        timestamp = msg.timestamp

        if state == "EMM_REGISTERED":
            if not self.current_lte_span:
                self.current_lte_span = [timestamp, None]
        else:
            if self.current_lte_span:
                self.current_lte_span[1] = timestamp
                self.lte_service_spans.append(tuple(self.current_lte_span))
                self.current_lte_span = None

    def __process_lte_rrc_ota_packet(self, msg):
        """
        Process LTE RRC OTA Packets for reconfiguration and PLMN search logging

        :param msg: the LTE RRC OTA Packet message
        """
        log_item = msg.data.decode()
        log_item_dict = dict(log_item)

        if 'Msg' in log_item_dict:
            log_xml = ET.XML(log_item_dict['Msg'])
            for proto in log_xml.iter('proto'):
                if proto.get('name') == "lte-rrc.rrcConnectionReconfiguration":
                    self.lte_rrc_reconfigs += 1
                if proto.get('name') == "lte-rrc.plmn-IdentityList-r11":
                    self.lte_plmn_searches += 1

    def __process_umts_nas_ota_packet(self, msg):
        """
        Process UMTS NAS OTA Packets for PLMN search logging

        :param msg: the UMTS NAS OTA Packet message
        """
        log_item = msg.data.decode()
        log_item_dict = dict(log_item)

        if 'Msg' in log_item_dict:
            log_xml = ET.XML(log_item_dict['Msg'])
            for proto in log_xml.iter('proto'):
                if proto.get('name') == "gsm_a.dtap" and proto.get('field', {}).get('showname', '').startswith("PLMN search"):
                    self.umts_plmn_searches += 1

    def get_umts_service_spans(self):
        """
        Retrieve UMTS normal service spans

        :returns: list of tuples with start and end times of UMTS service spans
        """
        return self.umts_service_spans

    def get_lte_service_spans(self):
        """
        Retrieve LTE normal service spans

        :returns: list of tuples with start and end times of LTE service spans
        """
        return self.lte_service_spans

    def get_umts_plmn_searches(self):
        """
        Retrieve the number of UMTS PLMN searches

        :returns: integer count of UMTS PLMN searches
        """
        return self.umts_plmn_searches

    def get_lte_plmn_searches(self):
        """
        Retrieve the number of LTE PLMN searches

        :returns: integer count of LTE PLMN searches
        """
        return self.lte_plmn_searches

    def get_lte_rrc_reconfigs(self):
        """
        Retrieve the number of LTE RRC reconfigurations

        :returns: integer count of LTE RRC reconfigurations
        """
        return self.lte_rrc_reconfigs
