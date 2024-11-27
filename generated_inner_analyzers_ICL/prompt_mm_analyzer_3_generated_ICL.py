
#!/usr/bin/python
# Filename: mm_analyzer_modified.py
"""
mm_analyzer_modified.py
A modified analyzer to monitor UMTS and LTE mobility management state changes with additional metrics.

Author: Assistant
"""

__all__ = ["MmAnalyzerModified"]

import xml.etree.ElementTree as ET
from mobile_insight.analyzer import Analyzer
import re
from datetime import datetime

class MmAnalyzerModified(Analyzer):
    """
    A modified analyzer to monitor and analyze UMTS and LTE network state changes.
    """
    def __init__(self):
        Analyzer.__init__(self)

        self.add_source_callback(self.__filter)
        
        self.umts_event_spans = {
            "normal_service": [],
            "plmn_search": [],
            "attach": [],
            "location_update": [],
            "routing_area_update": []
        }

        self.lte_event_spans = {
            "normal_service": [],
            "plmn_search": [],
            "attach": [],
            "tau": []
        }

        self.lte_configurations = {
            "tau_qos_info": [],
            "cell_reselection_to_umts": [],
            "drx_config": [],
            "tdd_config": []
        }

        self.current_state = {
            "umts": None,
            "lte": None
        }

    def set_source(self, source):
        """
        Set the trace source. Enable the cellular signaling messages.

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)
        source.enable_log_all()

    def __filter(self, msg):
        if msg.type_id in ["UMTS_NAS_GMM_State", "UMTS_NAS_OTA_Packet", "LTE_NAS_EMM_State", "LTE_NAS_OTA_Packet", "LTE_RRC_OTA_Packet", "WCDMA_RRC_OTA_Packet"]:
            log_item = msg.data.decode()
            log_xml = ET.fromstring(log_item.get('Msg', ''))
            self.__process_event(log_xml, msg.type_id)

    def __process_event(self, xml_msg, msg_type):
        if msg_type == "UMTS_NAS_GMM_State":
            self.__process_umts_nas_gmm_state(xml_msg)
        elif msg_type == "UMTS_NAS_OTA_Packet":
            self.__process_umts_nas_ota_packet(xml_msg)
        elif msg_type == "LTE_NAS_EMM_State":
            self.__process_lte_nas_emm_state(xml_msg)
        elif msg_type == "LTE_NAS_OTA_Packet":
            self.__process_lte_nas_ota_packet(xml_msg)
        elif msg_type == "LTE_RRC_OTA_Packet":
            self.__process_lte_rrc_ota_packet(xml_msg)
        elif msg_type == "WCDMA_RRC_OTA_Packet":
            self.__process_wcdma_rrc_ota_packet(xml_msg)

    def __process_umts_nas_gmm_state(self, xml_msg):
        for proto in xml_msg.iter('proto'):
            if proto.get('name') == "gsm_a.gm.gmm":
                for field in proto.iter('field'):
                    if field.get('name') == "gsm_a.gm.gmm.state":
                        state = field.get('showname')
                        self.__handle_umts_state(state)

    def __process_umts_nas_ota_packet(self, xml_msg):
        # Implement specific handling if needed
        pass

    def __process_lte_nas_emm_state(self, xml_msg):
        for proto in xml_msg.iter('proto'):
            if proto.get('name') == "nas-eps.emm.state":
                for field in proto.iter('field'):
                    if field.get('name') == "nas-eps.emm.state.type":
                        state = field.get('showname')
                        self.__handle_lte_state(state)

    def __process_lte_nas_ota_packet(self, xml_msg):
        # Implement specific handling if needed
        pass

    def __process_lte_rrc_ota_packet(self, xml_msg):
        # Implement specific handling if needed
        pass

    def __process_wcdma_rrc_ota_packet(self, xml_msg):
        # Implement specific handling if needed
        pass

    def __handle_umts_state(self, state):
        if state == "GMM-REGISTERED":
            self.__start_span(self.umts_event_spans["normal_service"])
        elif state == "GMM-DEREGISTERED":
            self.__end_span(self.umts_event_spans["normal_service"])
            self.__start_span(self.umts_event_spans["plmn_search"])

    def __handle_lte_state(self, state):
        if state == "EMM-REGISTERED":
            self.__start_span(self.lte_event_spans["normal_service"])
        elif state == "EMM-DEREGISTERED":
            self.__end_span(self.lte_event_spans["normal_service"])
            self.__start_span(self.lte_event_spans["plmn_search"])

    def __start_span(self, span_list):
        span_list.append({"start": datetime.now(), "end": None})

    def __end_span(self, span_list):
        if span_list and span_list[-1]["end"] is None:
            span_list[-1]["end"] = datetime.now()
