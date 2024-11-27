
#!/usr/bin/python
# Filename: lte_rlc_analyzer_modified.py
"""
A modified LTE RLC analyzer for link layer information with altered calculations.

Author: Modified
"""

from mobile_insight.analyzer.analyzer import *

__all__ = ["LteRlcAnalyzerModified"]

class LteRlcAnalyzerModified(Analyzer):

    def __init__(self):
        Analyzer.__init__(self)

        self.rb_info = {}  # Track Radio Bearer information
        self.uplink_data = 0  # Track uplink data bytes
        self.downlink_data = 0  # Track downlink data bytes

        self.add_source_callback(self.__msg_callback)

    def set_source(self, source):
        """
        Set the trace source. Enable the LTE RLC messages.

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)

        source.enable_log("LTE_RLC_UL_Config_Log_Packet")
        source.enable_log("LTE_RLC_DL_Config_Log_Packet")
        source.enable_log("LTE_RLC_UL_AM_All_PDU")
        source.enable_log("LTE_RLC_DL_AM_All_PDU")

    def __msg_callback(self, msg):

        if msg.type_id == "LTE_RLC_UL_Config_Log_Packet" or msg.type_id == "LTE_RLC_DL_Config_Log_Packet":
            self.__process_rlc_config(msg)

        elif msg.type_id == "LTE_RLC_UL_AM_All_PDU":
            self.__process_ul_pdu(msg)

        elif msg.type_id == "LTE_RLC_DL_AM_All_PDU":
            self.__process_dl_pdu(msg)

    def __process_rlc_config(self, msg):
        """
        Process RLC Config messages to update RB information.

        :param msg: the RLC Config message
        """
        log_item = msg.data.decode()

        if 'RBs' in log_item:
            rb_count = len(log_item['RBs'])
            self.log_info(f"Number of active RBs: {rb_count}")

            for rb in log_item['RBs']:
                rb_id = rb.get('RB ID')
                if rb.get('Release'):
                    if rb_id in self.rb_info:
                        del self.rb_info[rb_id]
                        self.log_info(f"Released RB ID: {rb_id}")
                else:
                    self.rb_info[rb_id] = rb
                    self.log_info(f"Active RB ID: {rb_id} Settings: {rb}")

    def __process_ul_pdu(self, msg):
        """
        Process uplink PDUs and accumulate data bytes with modification.

        :param msg: the uplink PDU message
        """
        log_item = msg.data.decode()

        if 'PDUs' in log_item:
            for pdu in log_item['PDUs']:
                data_bytes = pdu.get('Size', 0)
                modified_data_bytes = data_bytes * 1.10  # Increase by 10%
                self.uplink_data += modified_data_bytes
                self.log_info(f"Uplink data bytes (modified): {modified_data_bytes}")

    def __process_dl_pdu(self, msg):
        """
        Process downlink PDUs and accumulate data bytes with modification.

        :param msg: the downlink PDU message
        """
        log_item = msg.data.decode()

        if 'PDUs' in log_item:
            for pdu in log_item['PDUs']:
                data_bytes = pdu.get('Size', 0)
                modified_data_bytes = data_bytes * 0.90  # Decrease by 10%
                self.downlink_data += modified_data_bytes
                self.log_info(f"Downlink data bytes (modified): {modified_data_bytes}")
