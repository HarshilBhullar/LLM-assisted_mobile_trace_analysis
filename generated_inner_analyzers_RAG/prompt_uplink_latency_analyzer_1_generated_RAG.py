
#!/usr/bin/python
# Filename: modified_uplink_latency_analyzer.py
"""
A modified analyzer for monitoring uplink packet waiting and processing latency with additional metrics.

Author: [Your Name]
"""

from mobile_insight.analyzer.analyzer import *

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import time
import json
from datetime import datetime

class ModifiedUplinkLatencyAnalyzer(Analyzer):
    """
    A modified analyzer to monitor uplink packet waiting and processing latency with additional metrics
    """

    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)

        # Initialize variables for metrics
        self.fn = 1
        self.sfn = 1
        self.cum_err_block = {0: 0, 1: 0}
        self.cum_block = {0: 0, 1: 0}

        # MAC buffer and packet queue
        self.last_buffer = 0
        self.packet_queue = []

        # Stats
        self.all_packets = []
        self.tx_packets = []
        self.tmp_dict = {}

    def set_source(self, source):
        """
        Set the trace source and enable relevant logs.

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)
        source.enable_log("LTE_PHY_PUSCH_Tx_Report")
        source.enable_log("LTE_MAC_UL_Buffer_Status_Internal")

    def __f_time(self):
        """
        Get current frame time.
        """
        return self.fn * 10 + self.sfn

    def __f_time_diff(self, fn1, sfn1, fn2, sfn2):
        """
        Compute the frame time difference between two time points.
        """
        return (fn1 - fn2) * 10 + (sfn1 - sfn2)

    def __cmp_queues(self, pkt1, pkt2):
        """
        Compare two packets based on transmission type.
        """
        return pkt1['Tx Type'] - pkt2['Tx Type']

    def update_time(self, sys_fn, sub_fn):
        """
        Update the current frame and subframe time.
        """
        self.fn = sys_fn
        self.sfn = sub_fn

    def __msg_callback(self, msg):
        """
        Callback function to process messages and compute latencies.
        """
        if msg.type_id == "LTE_PHY_PUSCH_Tx_Report":
            log_item = msg.data.decode()
            self.fn = log_item['Frame Num']
            self.sfn = log_item['Subframe Num']

            for pkt in log_item['Subpackets']:
                if 'Samples' in pkt:
                    for sample in pkt['Samples']:
                        if 'PUSCH Tx Power' in sample:
                            sub_fn = sample['Sub FN']
                            sys_fn = sample['Sys FN']

                            if (sys_fn, sub_fn) in self.tmp_dict:
                                latency = self.__f_time_diff(self.fn, self.sfn, sys_fn, sub_fn)
                                self.all_packets.append({
                                    'Waiting Latency': self.tmp_dict[(sys_fn, sub_fn)]['Waiting Latency'],
                                    'Tx Latency': latency,
                                    'Retx Latency': 0
                                })
                                del self.tmp_dict[(sys_fn, sub_fn)]

        elif msg.type_id == "LTE_MAC_UL_Buffer_Status_Internal":
            log_item = msg.data.decode()
            sys_fn = log_item['Sys FN']
            sub_fn = log_item['Sub FN']

            self.update_time(sys_fn, sub_fn)

            for pkt in log_item['Subpackets']:
                if 'LCIDs' in pkt:
                    for lcid in pkt['LCIDs']:
                        if 'New bytes' in lcid:
                            new_bytes = lcid['New bytes']
                            self.tmp_dict[(sys_fn, sub_fn)] = {
                                'Waiting Latency': self.__f_time_diff(self.fn, self.sfn, sys_fn, sub_fn)
                            }
