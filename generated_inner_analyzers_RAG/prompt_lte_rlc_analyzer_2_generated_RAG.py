
#!/usr/bin/python
# Filename: modified_lte_rlc_analyzer.py
"""
A modified LTE RLC analyzer focusing on RB configurations and throughput calculations.

Author: [Your Name]
"""

from .analyzer import *

__all__ = ["ModifiedLteRlcAnalyzer"]

class ModifiedLteRlcAnalyzer(Analyzer):
    """
    An analyzer for LTE RLC with specific focus on RB configurations and throughput calculations.
    """

    def __init__(self):
        Analyzer.__init__(self)
        self.rbInfo = {}  # Stores information about each RB

    def set_source(self, source):
        """
        Set the trace source. Enable the LTE RLC messages.

        :param source: the trace source.
        :type source: trace collector
        """
        Analyzer.set_source(self, source)
        source.enable_log("LTE_RLC_UL_Config_Log_Packet")
        source.enable_log("LTE_RLC_DL_Config_Log_Packet")
        source.enable_log("LTE_RLC_UL_AM_All_PDU")
        source.enable_log("LTE_RLC_DL_AM_All_PDU")
        self.add_source_callback(self.__msg_callback)

    def __msg_callback(self, msg):
        """
        Handle message callbacks for RLC messages

        :param msg: the event (message) from the trace collector.
        """
        if msg.type_id == "LTE_RLC_UL_Config_Log_Packet" or msg.type_id == "LTE_RLC_DL_Config_Log_Packet":
            self.__process_config_packet(msg)

        elif msg.type_id == "LTE_RLC_UL_AM_All_PDU" or msg.type_id == "LTE_RLC_DL_AM_All_PDU":
            self.__calculate_throughput(msg)

    def __process_config_packet(self, msg):
        """
        Process configuration packets to track active and released RBs

        :param msg: the RLC configuration message
        """
        log_item = msg.data.decode()
        for rb in log_item.get('Active RBs', []):
            rb_id = rb['RB Cfg Index']
            if rb_id not in self.rbInfo:
                self.rbInfo[rb_id] = {'cumulativeData': 0, 'seqNums': [], 'ackNums': []}
            self.log_info(f"Active RB Config: {rb_id}")

        for rb in log_item.get('Released RBs', []):
            rb_id = rb['RB Cfg Index']
            if rb_id in self.rbInfo:
                del self.rbInfo[rb_id]
                self.log_info(f"Released RB Config: {rb_id}")

    def __calculate_throughput(self, msg):
        """
        Calculate cumulative data and throughput

        :param msg: the RLC PDU message
        """
        log_item = msg.data.decode()
        rb_id = log_item['RB Cfg Index']
        if rb_id in self.rbInfo:
            pdu_bytes = log_item['PDU Bytes']
            adjusted_data = pdu_bytes * 1.1  # Adjust calculations
            self.rbInfo[rb_id]['cumulativeData'] += adjusted_data

            timestamp = msg.timestamp
            throughput = adjusted_data / (timestamp - self.rbInfo[rb_id].get('lastTimestamp', timestamp))
            self.rbInfo[rb_id]['lastTimestamp'] = timestamp

            self.log_info(f"RB Config Index: {rb_id}, Timestamp: {timestamp}, Throughput: {throughput}")

