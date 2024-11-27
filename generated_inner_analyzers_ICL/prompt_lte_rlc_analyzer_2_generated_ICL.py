
#!/usr/bin/python
# Filename: modified_lte_rlc_analyzer.py
"""
Author: [Your Name]
"""

from .analyzer import *
import datetime

__all__ = ["ModifiedLteRlcAnalyzer"]

class ModifiedLteRlcAnalyzer(Analyzer):
    """
    Analyze the LTE RLC layer with modifications for link layer information,
    focusing on RB configurations and throughput calculations.
    """

    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)

        self.rbInfo = {}  # rb_config_idx -> {'cumulative_data': int, 'seq_nums': list, 'ack_nums': list}

    def set_source(self, source):
        """
        Set the trace source. Enable specific logs for LTE RLC analysis.

        :param source: the trace source.
        :type source: trace collector
        """
        Analyzer.set_source(self, source)

        source.enable_log("LTE_RLC_UL_Config_Log_Packet")
        source.enable_log("LTE_RLC_DL_Config_Log_Packet")
        source.enable_log("LTE_RLC_UL_AM_All_PDU")
        source.enable_log("LTE_RLC_DL_AM_All_PDU")

    def __msg_callback(self, msg):
        """
        Process messages for LTE RLC layer analysis.

        :param msg: the event (message) from the trace collector.
        """
        log_item = msg.data.decode()

        if msg.type_id == "LTE_RLC_UL_Config_Log_Packet" or msg.type_id == "LTE_RLC_DL_Config_Log_Packet":
            self.__process_rlc_config(log_item, msg.type_id)

        elif msg.type_id == "LTE_RLC_UL_AM_All_PDU" or msg.type_id == "LTE_RLC_DL_AM_All_PDU":
            self.__process_rlc_pdu(log_item, msg.type_id)

    def __process_rlc_config(self, log_item, type_id):
        """
        Process RLC configuration messages to track active and released RBs.

        :param log_item: the decoded log data.
        :param type_id: the type of log message.
        """
        for entry in log_item["RBs"]:
            rb_cfg_idx = entry["RbCfgIdx"]
            if type_id == "LTE_RLC_UL_Config_Log_Packet":
                if entry["RbMode"] == "AM" and entry["Action"] == "Add":
                    self.rbInfo.setdefault(rb_cfg_idx, {'cumulative_data': 0, 'seq_nums': [], 'ack_nums': []})
                elif entry["Action"] == "Release":
                    self.rbInfo.pop(rb_cfg_idx, None)

            elif type_id == "LTE_RLC_DL_Config_Log_Packet":
                if entry["RbMode"] == "AM" and entry["Action"] == "Add":
                    self.rbInfo.setdefault(rb_cfg_idx, {'cumulative_data': 0, 'seq_nums': [], 'ack_nums': []})
                elif entry["Action"] == "Release":
                    self.rbInfo.pop(rb_cfg_idx, None)

    def __process_rlc_pdu(self, log_item, type_id):
        """
        Process RLC PDUs to calculate cumulative data and throughput.

        :param log_item: the decoded log data.
        :param type_id: the type of log message.
        """
        for pdu in log_item["PDUs"]:
            rb_cfg_idx = pdu["RbCfgIdx"]
            if rb_cfg_idx in self.rbInfo:
                pdu_bytes = pdu["PDU Size"] * 1.1  # Adjust throughput calculation
                self.rbInfo[rb_cfg_idx]['cumulative_data'] += pdu_bytes

                if type_id == "LTE_RLC_UL_AM_All_PDU":
                    self.rbInfo[rb_cfg_idx]['seq_nums'].append(pdu["SN"])
                    self.__log_throughput(rb_cfg_idx, log_item["timestamp"], pdu_bytes)

                elif type_id == "LTE_RLC_DL_AM_All_PDU":
                    self.rbInfo[rb_cfg_idx]['ack_nums'].append(pdu["SN"])
                    self.__log_throughput(rb_cfg_idx, log_item["timestamp"], pdu_bytes)

    def __log_throughput(self, rb_cfg_idx, timestamp, pdu_bytes):
        """
        Log the calculated throughput for a specific RB configuration.

        :param rb_cfg_idx: the RB configuration index.
        :param timestamp: the timestamp of the log entry.
        :param pdu_bytes: the calculated PDU bytes.
        """
        self.log_info(f"RB Config Index: {rb_cfg_idx}, Timestamp: {timestamp}, Throughput: {pdu_bytes} bytes")
