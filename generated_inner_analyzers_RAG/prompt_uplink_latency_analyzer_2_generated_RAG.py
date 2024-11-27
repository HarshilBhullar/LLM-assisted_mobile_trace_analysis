
#!/usr/bin/python
# Filename: uplink_latency_analyzer_modified.py

"""
uplink_latency_analyzer_modified.py
An analyzer to monitor uplink packet waiting and processing latency with additional metrics

Author: Modified by OpenAI
"""

__all__ = ["UplinkLatencyAnalyzerModified"]

from mobile_insight.analyzer.analyzer import *

class UplinkLatencyAnalyzerModified(Analyzer):

    def __init__(self):
        Analyzer.__init__(self)

        self.add_source_callback(self.__msg_callback)
        
        # Timers
        self.fn = 1
        self.sfn = 1

        # PHY stats
        self.cum_err_block = {0: 0, 1: 0}  # 0 for uplink, 1 for downlink
        self.cum_block = {0: 0, 1: 0}  # 0 for uplink, 1 for downlink
        self.cum_retx_latency = 0

        # MAC buffer
        self.last_buffer = 0
        self.packet_queue = []

        # Stats
        self.all_packets = []
        self.tx_packets = []
        self.tmp_dict = {}

    def set_source(self, source):
        Analyzer.set_source(self, source)
        source.enable_log("LTE_PHY_PUSCH_Tx_Report")
        source.enable_log("LTE_MAC_UL_Buffer_Status_Internal")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_PHY_PUSCH_Tx_Report":
            self.__process_pusch_tx_report(msg)
        elif msg.type_id == "LTE_MAC_UL_Buffer_Status_Internal":
            self.__process_mac_ul_buffer_status(msg)

    def __process_pusch_tx_report(self, msg):
        log_item = msg.data.decode()
        if 'Subpackets' in log_item:
            for pkt in log_item['Subpackets']:
                for tb in pkt['Samples']:
                    self.cum_block[0] += 1
                    if not tb['ACK']:
                        self.cum_err_block[0] += 1
                        self.cum_retx_latency += tb['Re-tx Latency'] if 'Re-tx Latency' in tb else 0

    def __process_mac_ul_buffer_status(self, msg):
        log_item = msg.data.decode()
        if 'Subpackets' in log_item:
            for pkt in log_item['Subpackets']:
                if 'Samples' in pkt:
                    for sample in pkt['Samples']:
                        self.__update_packet_queue(sample)

    def __update_packet_queue(self, sample):
        current_buffer = int(sample['Total Bytes'])
        current_sn = sample['Sys FN'] * 10 + sample['Sub FN']
        delta_buffer = current_buffer - self.last_buffer

        if delta_buffer > 0:
            self.packet_queue.append({
                'timestamp': current_sn,
                'size': delta_buffer,
                'waiting_latency': 0,
                'tx_latency': 0,
                'retx_latency': 0
            })
        elif delta_buffer < 0:
            self.__update_packet_latencies(-delta_buffer, current_sn)

        self.last_buffer = current_buffer

    def __update_packet_latencies(self, bytes_sent, current_sn):
        while bytes_sent > 0 and self.packet_queue:
            packet = self.packet_queue[0]
            if packet['size'] <= bytes_sent:
                bytes_sent -= packet['size']
                packet['tx_latency'] = current_sn - packet['timestamp']
                packet['waiting_latency'] = 0  # Assuming immediate processing after dequeuing
                self.all_packets.append(packet)
                self.packet_queue.pop(0)
            else:
                packet['size'] -= bytes_sent
                bytes_sent = 0

    def calculate_average_latencies(self):
        total_latency = 0
        total_wait = 0
        total_trans = 0
        total_retx = 0

        for packet in self.all_packets:
            total_wait += packet['waiting_latency']
            total_trans += packet['tx_latency']
            total_retx += packet['retx_latency']

        total_latency = total_wait + total_trans + total_retx
        n = len(self.all_packets)

        if n > 0:
            return {
                'average_latency': float(total_latency) / n,
                'average_waiting_latency': float(total_wait) / n,
                'average_tx_latency': float(total_trans) / n,
                'average_retx_latency': float(total_retx) / n
            }
        else:
            return None
