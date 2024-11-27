
#!/usr/bin/python
# Filename: umts_nas_analyzer_modified.py
"""
A modified analyzer for UMTS NAS layer (MM/GMM/CM) packets with additional metrics.

Author: Yuanjie Li
Modified by: [Your Name]
"""

from .analyzer import ProtocolAnalyzer

__all__ = ["UmtsNasAnalyzerModified"]

class UmtsNasAnalyzerModified(ProtocolAnalyzer):
    """
    A modified analyzer for UMTS NAS layer (MM/GMM/CM) packets with additional metrics.
    """

    def __init__(self):
        ProtocolAnalyzer.__init__(self)

        self.add_source_callback(self.__nas_filter)

        # State machine attributes
        self.mm_state = "Idle"
        self.gmm_state = "Deregistered"
        self.cm_state = "Idle"

        # QoS and DRX parameters
        self.qos_params = {}
        self.drx_params = {}

    def set_source(self, source):
        ProtocolAnalyzer.set_source(self, source)
        source.enable_log("UMTS_NAS_OTA_Packet")
        source.enable_log("UMTS_NAS_GMM_State")
        source.enable_log("UMTS_NAS_MM_State")

    def __nas_filter(self, msg):
        if msg.type_id == "UMTS_NAS_MM_State":
            self.__callback_mm_state(msg)
        elif msg.type_id == "UMTS_NAS_GMM_State":
            self.__callback_gmm_state(msg)
        elif msg.type_id == "UMTS_NAS_OTA_Packet":
            self.__callback_nas(msg)

    def __callback_mm_state(self, msg):
        log_item = msg.data.decode()
        new_state = log_item.get("MM State", "Unknown")
        if new_state != self.mm_state:
            self.mm_state = new_state
            self.broadcast_info("MM_STATE", {"state": self.mm_state})
            self.log_info(f"MM State changed to: {self.mm_state}")

    def __callback_gmm_state(self, msg):
        log_item = msg.data.decode()
        new_state = log_item.get("GMM State", "Unknown")
        if new_state != self.gmm_state:
            self.gmm_state = new_state
            self.broadcast_info("GMM_STATE", {"state": self.gmm_state})
            self.log_info(f"GMM State changed to: {self.gmm_state}")

    def __callback_nas(self, msg):
        log_item = msg.data.decode()
        self.__update_cm_state(log_item)
        self.__update_qos_params(log_item)
        self.__update_drx_params(log_item)

    def __update_cm_state(self, log_item):
        # Example CM state update logic
        if "Service Request" in log_item:
            self.cm_state = "Service Requested"
        elif "Setup" in log_item:
            self.cm_state = "Setup"
        elif "Call Proceeding" in log_item:
            self.cm_state = "Call Proceeding"
        elif "Alerting" in log_item:
            self.cm_state = "Alerting"
        elif "Connect" in log_item:
            self.cm_state = "Connected"
        elif "Disconnect" in log_item:
            self.cm_state = "Disconnected"
        self.log_info(f"CM State: {self.cm_state}")

    def __update_qos_params(self, log_item):
        # Example QoS parameters update logic
        self.qos_params["delay_class"] = log_item.get("Delay Class", "Unknown")
        self.qos_params["reliability_class"] = log_item.get("Reliability Class", "Unknown")
        self.qos_params["throughput_class"] = log_item.get("Throughput Class", "Unknown")
        self.log_info(f"QoS Parameters: {self.qos_params}")

    def __update_drx_params(self, log_item):
        # Example DRX parameters update logic
        self.drx_params["DRX Cycle Length"] = log_item.get("DRX Cycle Length", "Unknown")
        self.log_info(f"DRX Parameters: {self.drx_params}")

    def create_profile_hierarchy(self):
        # Example profile hierarchy creation logic
        return {
            "MM State": self.mm_state,
            "GMM State": self.gmm_state,
            "CM State": self.cm_state,
            "QoS Parameters": self.qos_params,
            "DRX Parameters": self.drx_params
        }
