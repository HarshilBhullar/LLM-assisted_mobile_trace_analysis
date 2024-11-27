
#!/usr/bin/python
# Filename: modified_lte_mac_analyzer.py

"""
modified_lte_mac_analyzer.py
Enhanced analyzer for LTE MAC-layer packets with additional analysis functions

Author: Modified by Assistant
"""

__all__ = ["ModifiedLteMacAnalyzer"]

from mobile_insight.analyzer.analyzer import *

class ModifiedLteMacAnalyzer(Analyzer):
    """
    A modified analyzer to enhance analysis functions for LTE MAC-layer packets
    """

    def __init__(self):
        Analyzer.__init__(self)

        self.add_source_callback(self.__msg_callback)
        self.ul_grant_utilization = {}
        self.ul_control_pkt_delay = []
        self.queue_length = 0
        self.harq_failures = 0
        self.retx_delays = []

    def set_source(self, source):
        """
        Set the trace source. Enable the cellular signaling messages

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)

        source.enable_log("LTE_MAC_UL_Tx_Statistics")
        source.enable_log("LTE_MAC_UL_Buffer_Status_Internal")
        source.enable_log("LTE_PHY_PDSCH_Stat_Indication")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_MAC_UL_Tx_Statistics":
            log_item = msg.data.decode()
            grant_util = self.__calculate_ul_grant_utilization(log_item)
            self.ul_grant_utilization[msg.timestamp] = grant_util
            self.broadcast_info("UL_GRANT_UTILIZATION", {"timestamp": str(msg.timestamp), "utilization": grant_util})

        elif msg.type_id == "LTE_MAC_UL_Buffer_Status_Internal":
            log_item = msg.data.decode()
            delay = self.__calculate_ul_control_pkt_delay(log_item)
            self.ul_control_pkt_delay.append(delay)
            self.broadcast_info("UL_CONTROL_PKT_DELAY", {"timestamp": str(msg.timestamp), "delay": delay})

        elif msg.type_id == "LTE_PHY_PDSCH_Stat_Indication":
            log_item = msg.data.decode()
            self.harq_failures += self.__count_harq_failures(log_item)
            retx_delay = self.__calculate_retx_delay(log_item)
            self.retx_delays.append(retx_delay)
            self.broadcast_info("RETX_DELAY", {"timestamp": str(msg.timestamp), "delay": retx_delay})

    def __calculate_ul_grant_utilization(self, log_item):
        # Custom logic to calculate UL grant utilization
        total_grant = sum([item['grant'] for item in log_item.get('Records', [])])
        utilized_grant = sum([item['used_grant'] for item in log_item.get('Records', [])])
        return utilized_grant / total_grant if total_grant > 0 else 0

    def __calculate_ul_control_pkt_delay(self, log_item):
        # Custom logic to calculate UL control packet delay
        delays = []
        for sample in log_item.get('Samples', []):
            ctrl_bytes = sample.get('Ctrl bytes', 0)
            if ctrl_bytes > 0:
                delays.append(sample['timestamp'])
        return max(delays) - min(delays) if delays else 0

    def __count_harq_failures(self, log_item):
        # Custom logic to count HARQ failures
        return sum(1 for harq in log_item.get('HARQ', []) if harq['status'] == 'fail')

    def __calculate_retx_delay(self, log_item):
        # Custom logic to calculate retransmission delay
        delays = [retx['delay'] for retx in log_item.get('HARQ', []) if retx['status'] == 'success']
        return sum(delays) / len(delays) if delays else 0
