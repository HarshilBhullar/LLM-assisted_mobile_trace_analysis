
#!/usr/bin/python
# Filename: lte_mac_analyzer_modified.py

"""
A modified 4G MAC-layer analyzer with additional metric evaluations.

Author: Assistant
"""

from mobile_insight.analyzer.analyzer import Analyzer
import xml.etree.ElementTree as ET

__all__ = ["LteMacAnalyzerModified"]

class LteMacAnalyzerModified(Analyzer):
    """
    A modified protocol analyzer for 4G MAC layer.
    """

    def __init__(self):
        Analyzer.__init__(self)

        # Initialize internal states
        self.ul_grant_utilization = []
        self.mac_buffer_status = []
        self.harq_failures = 0

        # Set up source callbacks
        self.add_source_callback(self.__msg_callback)

    def set_source(self, source):
        """
        Set the trace source and enable specific MAC layer logs.

        :param source: the trace source.
        :type source: trace collector
        """
        Analyzer.set_source(self, source)
        source.enable_log("LTE_MAC_UL_Tx_Statistics")
        source.enable_log("LTE_MAC_UL_Buffer_Status_Internal")
        source.enable_log("LTE_PHY_PDSCH_Stat_Indication")

    def __msg_callback(self, msg):
        """
        Process relevant log packets and extract, calculate, and log necessary information.
        
        :param msg: the event (message) from the trace collector.
        """
        log_item = msg.data.decode()
        log_item_dict = dict(log_item)

        if msg.type_id == "LTE_MAC_UL_Tx_Statistics":
            self.__process_ul_tx_statistics(log_item_dict)
        elif msg.type_id == "LTE_MAC_UL_Buffer_Status_Internal":
            self.__process_mac_buffer_status(log_item_dict)
        elif msg.type_id == "LTE_PHY_PDSCH_Stat_Indication":
            self.__process_harq_failures(log_item_dict)

    def __process_ul_tx_statistics(self, log_item):
        # Calculate UL grant utilization
        utilized_grant = log_item['Num Grants'] - log_item['Num ReTx']
        total_grant = log_item['Num Grants']
        utilization = utilized_grant / total_grant if total_grant > 0 else 0

        # Calculate and log variance if applicable
        self.ul_grant_utilization.append(utilization)
        if len(self.ul_grant_utilization) > 1:
            variance = sum((x - utilization) ** 2 for x in self.ul_grant_utilization) / len(self.ul_grant_utilization)
            self.log_info("UL Grant Utilization Variance: {}".format(variance))

        self.broadcast_info("UL_GRANT_UTILIZATION", {"utilization": utilization})

    def __process_mac_buffer_status(self, log_item):
        # Analyze buffer status and packet delays
        buffer_occupancy = log_item['Buffer Occupancy']
        self.mac_buffer_status.append(buffer_occupancy)

        self.broadcast_info("MAC_BUFFER_STATUS", {"buffer_occupancy": buffer_occupancy})

    def __process_harq_failures(self, log_item):
        # Track HARQ failures
        harq_failure = log_item['HARQ Failures']
        self.harq_failures += harq_failure

        self.broadcast_info("HARQ_FAILURES", {"harq_failures": self.harq_failures})
