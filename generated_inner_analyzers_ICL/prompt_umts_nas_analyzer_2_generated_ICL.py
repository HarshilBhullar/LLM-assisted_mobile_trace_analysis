
#!/usr/bin/python
# Filename: umts_nas_analyzer_modified.py
"""
A modified analyzer for UMTS NAS (MM/GMM/CM/SM) layer analysis

Author: Modified
"""

from mobile_insight.analyzer.analyzer import ProtocolAnalyzer

__all__ = ["UmtsNasAnalyzerModified"]

class UmtsNasAnalyzerModified(ProtocolAnalyzer):

    def __init__(self):
        ProtocolAnalyzer.__init__(self)

        self.add_source_callback(self.__nas_filter)

        # Initialize state machines for MM, GMM, and CM
        self.mm_state = 'MM_IDLE'
        self.gmm_state = 'GMM_DEREGISTERED'
        self.cm_state = 'CM_IDLE'

    def set_source(self, source):
        """
        Set the trace source. Enable the NAS messages

        :param source: the trace source (collector).
        """
        ProtocolAnalyzer.set_source(self, source)
        source.enable_log("UMTS_NAS_MM_State")
        source.enable_log("UMTS_NAS_GMM_State")
        source.enable_log("UMTS_NAS_OTA_Packet")

    def __nas_filter(self, msg):

        log_item = msg.data.decode()

        if msg.type_id == "UMTS_NAS_MM_State":
            new_state = log_item.get('MM State', None)
            if new_state and new_state != self.mm_state:
                self.mm_state = new_state
                self.log_info(f"MM State changed to: {self.mm_state}")
                self.broadcast_info('MM_STATE', {'state': self.mm_state})

        elif msg.type_id == "UMTS_NAS_GMM_State":
            new_state = log_item.get('GMM State', None)
            if new_state and new_state != self.gmm_state:
                self.gmm_state = new_state
                self.log_info(f"GMM State changed to: {self.gmm_state}")
                self.broadcast_info('GMM_STATE', {'state': self.gmm_state})

        elif msg.type_id == "UMTS_NAS_OTA_Packet":
            cm_event = log_item.get('CM Service Request', None)
            if cm_event:
                self.cm_state = 'CM_SERVICE_REQUEST'
                self.log_info(f"CM State changed to: {self.cm_state}")
                self.broadcast_info('CM_STATE', {'state': self.cm_state})

            # Additional CM state transitions based on message content
            cm_setup = log_item.get('CM Setup', None)
            if cm_setup:
                self.cm_state = 'CM_SETUP'
                self.log_info(f"CM State changed to: {self.cm_state}")
                self.broadcast_info('CM_STATE', {'state': self.cm_state})

            cm_call_proc = log_item.get('CM Call Proceeding', None)
            if cm_call_proc:
                self.cm_state = 'CM_CALL_PROCEEDING'
                self.log_info(f"CM State changed to: {self.cm_state}")
                self.broadcast_info('CM_STATE', {'state': self.cm_state})

        # Capture and broadcast additional parameters like QoS, DRX, etc.
        qos_params = log_item.get('QoS', None)
        if qos_params:
            self.broadcast_info('QoS_PARAMETERS', {'qos': qos_params})
            self.log_info(f"QoS parameters updated: {qos_params}")

        drx_params = log_item.get('DRX', None)
        if drx_params:
            self.broadcast_info('DRX_PARAMETERS', {'drx': drx_params})
            self.log_info(f"DRX parameters updated: {drx_params}")
