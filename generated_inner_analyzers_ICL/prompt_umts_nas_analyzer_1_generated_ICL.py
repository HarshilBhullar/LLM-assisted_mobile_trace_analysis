
#!/usr/bin/python
# Filename: umts_nas_analyzer_modified.py
"""
A modified UMTS NAS analyzer for analyzing MM/GMM/CM/SM packets and reporting additional metrics.

Author: [Your Name]
"""

from mobile_insight.analyzer.analyzer import *
from mobile_insight.analyzer.protocol_analyzer import *
import xml.etree.ElementTree as ET

__all__ = ["UmtsNasAnalyzerModified"]

class UmtsNasAnalyzerModified(ProtocolAnalyzer):
    """
    A protocol analyzer for UMTS NAS layer (MM/GMM/CM/SM) packets with modifications.
    """

    def __init__(self):
        ProtocolAnalyzer.__init__(self)
        
        self.add_source_callback(self.__nas_filter)

        # Initialize state machines for MM, GMM, CM
        self.mm_state = None
        self.gmm_state = None
        self.cm_state = None

        # QoS and DRX parameters
        self.qos_profile = {}
        self.drx_parameters = {}

    def set_source(self, source):
        """
        Set the trace source. Enable UMTS NAS messages.

        :param source: the trace source.
        :type source: trace collector
        """
        Analyzer.set_source(self, source)
        source.enable_log("UMTS_NAS_OTA_Packet")
        source.enable_log("UMTS_NAS_GMM_State")
        source.enable_log("UMTS_NAS_MM_State")

    def __nas_filter(self, msg):
        """
        Filter all UMTS NAS packets and call functions to process them.

        :param msg: the event (message) from the trace collector.
        """
        log_item = msg.data.decode()
        log_item_dict = dict(log_item)

        if msg.type_id == "UMTS_NAS_OTA_Packet":
            self.__callback_nas(log_item_dict)

        elif msg.type_id == "UMTS_NAS_MM_State":
            self.__callback_mm_state(log_item_dict)
            self.__callback_mm_reg_state(log_item_dict)

        elif msg.type_id == "UMTS_NAS_GMM_State":
            self.__callback_gmm_state(log_item_dict)

    def __callback_mm_state(self, log_item_dict):
        """
        Update MM state based on UMTS_NAS_MM_State messages.

        :param log_item_dict: the decoded message
        """
        state = log_item_dict.get("MM State", None)
        if state != self.mm_state:
            self.mm_state = state
            self.log_info(f"MM state transitioned to {self.mm_state}")

    def __callback_mm_reg_state(self, log_item_dict):
        """
        Update MM registration attributes from MM registration state messages.

        :param log_item_dict: the decoded message
        """
        plmn = log_item_dict.get('PLMN', None)
        lac = log_item_dict.get('LAC', None)
        rac = log_item_dict.get('RAC', None)
        self.log_info(f"MM registration state: PLMN={plmn}, LAC={lac}, RAC={rac}")

    def __callback_gmm_state(self, log_item_dict):
        """
        Update and broadcast GMM state information.

        :param log_item_dict: the decoded message
        """
        state = log_item_dict.get("GMM State", None)
        if state != self.gmm_state:
            self.gmm_state = state
            self.log_info(f"GMM state transitioned to {self.gmm_state}")

    def __callback_nas(self, log_item_dict):
        """
        Extract MM status and configurations from NAS messages and update status.

        :param log_item_dict: the decoded message
        """
        # Handle CM state transitions
        if 'CM Service Type' in log_item_dict:
            cm_service_type = log_item_dict['CM Service Type']
            self.cm_state = cm_service_type
            self.log_info(f"CM state: {self.cm_state}")

        # Extract QoS parameters
        if 'QoS Parameters' in log_item_dict:
            self.qos_profile = log_item_dict['QoS Parameters']
            self.log_info(f"QoS Profile updated: {self.qos_profile}")

        # Extract DRX parameters
        if 'DRX Parameters' in log_item_dict:
            self.drx_parameters = log_item_dict['DRX Parameters']
            self.log_info(f"DRX Parameters updated: {self.drx_parameters}")

    def create_profile_hierarchy(self):
        """
        Return a UMTS NAS ProfileHierarchy for managing configurations.
        """
        return {
            'MM State': self.mm_state,
            'GMM State': self.gmm_state,
            'CM State': self.cm_state,
            'QoS Profile': self.qos_profile,
            'DRX Parameters': self.drx_parameters
        }
