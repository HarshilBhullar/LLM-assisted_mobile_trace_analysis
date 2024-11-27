
#!/usr/bin/python
# Filename: modified_mm_analyzer.py

"""
Function: Adjusted metrics for MM state changes with additional analysis
Author: Your Name
"""

from mobile_insight.analyzer.analyzer import *
import xml.etree.ElementTree as ET
from datetime import datetime

__all__ = ["ModifiedMmAnalyzer"]

class ModifiedMmAnalyzer(Analyzer):

    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)

        self.umts_logs = []
        self.lte_logs = []
        self.lte_plmn_search_count = 0

    def set_source(self, source):
        Analyzer.set_source(self, source)
        source.enable_log("UMTS_NAS_GMM_State")
        source.enable_log("LTE_NAS_EMM_State")
        source.enable_log("LTE_RRC_OTA_Packet")
        source.enable_log("UMTS_NAS_OTA_Packet")

    def __msg_callback(self, msg):
        if msg.type_id == "UMTS_NAS_GMM_State":
            self.__process_umts_gmm_state(msg)

        if msg.type_id == "LTE_NAS_EMM_State":
            self.__process_lte_emm_state(msg)

        if msg.type_id == "LTE_RRC_OTA_Packet":
            self.__process_lte_rrc_ota_packet(msg)

        if msg.type_id == "UMTS_NAS_OTA_Packet":
            self.__process_umts_nas_ota_packet(msg)

    def __process_umts_gmm_state(self, msg):
        log_item = msg.data.decode()
        state = log_item.get("GMM State", "UNKNOWN")
        timestamp = log_item.get("timestamp", datetime.now().isoformat())
        self.umts_logs.append((timestamp, state))

    def __process_lte_emm_state(self, msg):
        log_item = msg.data.decode()
        state = log_item.get("EMM State", "UNKNOWN")
        timestamp = log_item.get("timestamp", datetime.now().isoformat())
        self.lte_logs.append((timestamp, state))

    def __process_lte_rrc_ota_packet(self, msg):
        log_item = msg.data.decode()
        log_xml = ET.XML(log_item['Msg'])
        for proto in log_xml.iter('proto'):
            if proto.get('name') == "lte-rrc":
                if "Reconfiguration" in proto.get('showname', ''):
                    self.lte_plmn_search_count += 1

    def __process_umts_nas_ota_packet(self, msg):
        log_item = msg.data.decode()
        log_xml = ET.XML(log_item['Msg'])
        for proto in log_xml.iter('proto'):
            if proto.get('name') == "umts-nas":
                pass  # Placeholder for future processing

    def get_umts_logs(self):
        return self.umts_logs

    def get_lte_logs(self):
        return self.lte_logs

    def get_lte_plmn_search_count(self):
        return self.lte_plmn_search_count

    def get_log_summary(self):
        return {
            "UMTS Logs": len(self.umts_logs),
            "LTE Logs": len(self.lte_logs),
            "LTE PLMN Searches": self.lte_plmn_search_count
        }
