
#!/usr/bin/python
# Filename: modified_lte_mac_analyzer.py
"""
Modified LTE MAC Analyzer for enhanced LTE MAC-layer analysis

Author: Yuanjie Li
Modified by: [Your Name]
"""

from mobile_insight.analyzer.analyzer import *

__all__ = ["ModifiedLteMacAnalyzer"]


class ModifiedLteMacAnalyzer(Analyzer):

    def __init__(self):
        Analyzer.__init__(self)
        self.ul_grant_utilization = 0
        self.packet_delays = {}
        self.queue_lengths = {}
        self.harq_failures = {}
        self.retransmission_delays = {}

        self.add_source_callback(self.__msg_callback)

    def set_source(self, source):
        """
        Set the trace source. Enable the LTE MAC-layer messages

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)

        # Enable necessary LTE MAC-layer logs
        source.enable_log("LTE_MAC_UL_Tx_Statistics")
        source.enable_log("LTE_MAC_UL_Buffer_Status_Internal")
        source.enable_log("LTE_PHY_PDSCH_Stat_Indication")

    def __msg_callback(self, msg):

        if msg.type_id == "LTE_MAC_UL_Tx_Statistics":
            self.__process_ul_tx_statistics(msg)
        elif msg.type_id == "LTE_MAC_UL_Buffer_Status_Internal":
            self.__process_ul_buffer_status(msg)
        elif msg.type_id == "LTE_PHY_PDSCH_Stat_Indication":
            self.__process_pdsch_stat_indication(msg)

    def __process_ul_tx_statistics(self, msg):
        # Enhanced UL grant utilization calculation
        log_item = msg.data.decode()
        ul_grant_util = log_item.get("UL Grant Utilization", 0) * 1.05  # Example modification
        self.ul_grant_utilization = ul_grant_util
        self.broadcast_info(f"UL Grant Utilization: {self.ul_grant_utilization}")
        self.log_info(f"UL Grant Utilization: {self.ul_grant_utilization}")

    def __process_ul_buffer_status(self, msg):
        # Maintain buffer and compute delays for UL control packets
        log_item = msg.data.decode()
        packet_id = log_item.get("Packet ID")
        buffer_status = log_item.get("Buffer Status")

        self.packet_delays[packet_id] = buffer_status / 10  # Example delay calculation
        self.queue_lengths[packet_id] = buffer_status
        self.broadcast_info(f"Packet ID: {packet_id}, Delay: {self.packet_delays[packet_id]}, Queue Length: {self.queue_lengths[packet_id]}")
        self.log_info(f"Packet ID: {packet_id}, Delay: {self.packet_delays[packet_id]}, Queue Length: {self.queue_lengths[packet_id]}")

    def __process_pdsch_stat_indication(self, msg):
        # Track HARQ failures and compute retransmission delays
        log_item = msg.data.decode()
        harq_id = log_item.get("HARQ ID")
        harq_failures = log_item.get("HARQ Failures", 0)
        retransmission_delay = log_item.get("Retransmission Delay", 0) * 1.1  # Example modification

        self.harq_failures[harq_id] = harq_failures
        self.retransmission_delays[harq_id] = retransmission_delay
        self.broadcast_info(f"HARQ ID: {harq_id}, Failures: {self.harq_failures[harq_id]}, Retransmission Delay: {self.retransmission_delays[harq_id]}")
        self.log_info(f"HARQ ID: {harq_id}, Failures: {self.harq_failures[harq_id]}, Retransmission Delay: {self.retransmission_delays[harq_id]}")
