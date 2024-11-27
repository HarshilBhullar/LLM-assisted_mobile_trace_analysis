
#!/usr/bin/python
# Filename: uplink_latency_analyzer_modified.py

"""
uplink_latency_analyzer_modified.py
An analyzer to monitor uplink packet waiting and processing latency with modified calculations

Author: MobileInsight Team (Modified by Assistant)
"""

import xml.etree.ElementTree as ET
from .analyzer import *

__all__ = ["UplinkLatencyAnalyzerModified"]

class UplinkLatencyAnalyzerModified(Analyzer):
    """
    A modified analyzer to monitor uplink latency breakdown with additional metrics
    """

    def __init__(self):
        Analyzer.__init__(self)

        self.add_source_callback(self.__msg_callback)

        self.cum_err_block = [0]
        self.cum_block = 0
        self.all_packets = []
        self.packet_queue = []
        self.retx_latency = 0  # New variable to track cumulative retransmission latency

    def set_source(self, source):
        """
        Set the trace source. Enable the cellular signaling messages

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)

        source.enable_log("LTE_PHY_PUSCH_Tx_Report")
        source.enable_log("LTE_MAC_UL_Buffer_Status_Internal")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_PHY_PUSCH_Tx_Report":
            self.__process_pusch_tx_report(msg)

        if msg.type_id == "LTE_MAC_UL_Buffer_Status_Internal":
            self.__process_ul_buffer_status(msg)

    def __process_pusch_tx_report(self, msg):
        log_item = msg.data.decode()
        if 'Records' in log_item:
            for record in log_item['Records']:
                if 'SubPackets' in record:
                    for subpacket in record['SubPackets']:
                        if 'Samples' in subpacket:
                            for sample in subpacket['Samples']:
                                if 'Grant (bytes)' in sample:
                                    grant_size = sample['Grant (bytes)']
                                    self.cum_block += grant_size

                                if 'BLER' in sample:
                                    bler = sample['BLER']
                                    if bler > 0:
                                        self.cum_err_block[0] += 1
                                        self.retx_latency += bler * 8  # Update retransmission latency

    def __process_ul_buffer_status(self, msg):
        log_item = msg.data.decode()
        if 'Subpackets' in log_item:
            for subpacket in log_item['Subpackets']:
                if 'Samples' in subpacket:
                    for sample in subpacket['Samples']:
                        sub_fn = int(sample['Sub FN'])
                        sys_fn = int(sample['Sys FN'])

                        for lcid in sample['LCIDs']:
                            new_bytes = int(lcid['New bytes']) if 'New bytes' in lcid else 0
                            ctrl_bytes = int(lcid['Ctrl bytes']) if 'Ctrl bytes' in lcid else 0

                            if new_bytes > 0:
                                self.__add_packet_to_queue((sys_fn, sub_fn), new_bytes, ctrl_bytes)

                            self.__process_packet_queue((sys_fn, sub_fn), new_bytes, ctrl_bytes)

    def __add_packet_to_queue(self, fn_tuple, new_bytes, ctrl_bytes):
        self.packet_queue.append({'fn_tuple': fn_tuple, 'new_bytes': new_bytes, 'ctrl_bytes': ctrl_bytes})

    def __process_packet_queue(self, fn_tuple, new_bytes, ctrl_bytes):
        waiting_latency = 0
        tx_latency = 0

        while self.packet_queue:
            packet = self.packet_queue[0]
            packet_fn_tuple = packet['fn_tuple']

            diff = self.__calculate_time_diff(packet_fn_tuple, fn_tuple)

            if diff > 0:
                waiting_latency += diff
                self.packet_queue.pop(0)

                self.all_packets.append({'Waiting Latency': waiting_latency, 'Tx Latency': tx_latency, 'Retx Latency': self.retx_latency})

    def __calculate_time_diff(self, start_fn, end_fn):
        start_sys_fn, start_sub_fn = start_fn
        end_sys_fn, end_sub_fn = end_fn

        if end_sys_fn < start_sys_fn:
            end_sys_fn += 10240

        time_diff = (end_sys_fn * 10 + end_sub_fn) - (start_sys_fn * 10 + start_sub_fn)
        return time_diff
