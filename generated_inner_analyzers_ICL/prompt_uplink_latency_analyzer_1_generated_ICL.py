
#!/usr/bin/python
# Filename: modified_uplink_latency_analyzer.py

"""
Function: Monitor uplink packet waiting and processing latency with additional metrics
"""

from mobile_insight.analyzer.analyzer import *
import datetime
import sys

__all__ = ["ModifiedUplinkLatencyAnalyzer"]

class ModifiedUplinkLatencyAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)

        self.fn = 0
        self.sfn = 0
        self.cum_err_block = [0]
        self.cum_block = [0]
        self.mac_buffer = []
        self.all_packets = []
        self.tx_packets = []
        self.temp_dict = {}

    def set_source(self, source):
        Analyzer.set_source(self, source)
        source.enable_log("LTE_PHY_PUSCH_Tx_Report")
        source.enable_log("LTE_MAC_UL_Buffer_Status_Internal")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_PHY_PUSCH_Tx_Report":
            self.__process_pusch_tx_report(msg)

        if msg.type_id == "LTE_MAC_UL_Buffer_Status_Internal":
            self.__process_mac_ul_buffer_status(msg)

    def __process_pusch_tx_report(self, msg):
        log_item = msg.data.decode()
        for report in log_item['Records']:
            subfn = report['Sub FN']
            sysfn = report['Sys FN']
            sn = report['PUSCH Tx Power']
            if sn in self.temp_dict:
                latency_info = self.temp_dict.pop(sn)
                latency_info['Retx Latency'] = self.__f_time_diff(self.__f_time(sysfn, subfn), latency_info['Retx Start'])
                self.all_packets.append(latency_info)
            else:
                self.cum_err_block[0] += 1

    def __process_mac_ul_buffer_status(self, msg):
        log_item = msg.data.decode()
        sysfn = log_item['Sys FN']
        subfn = log_item['Sub FN']
        self.update_time(sysfn, subfn)

        for buffer in log_item['Buffers']:
            packet_id = buffer['Packet ID']
            if packet_id not in self.temp_dict:
                self.temp_dict[packet_id] = {
                    'Waiting Latency': 0,
                    'Tx Latency': 0,
                    'Retx Start': self.__f_time(self.fn, self.sfn)
                }
            else:
                self.temp_dict[packet_id]['Waiting Latency'] += 1

        self.__cmp_queues()

    def __f_time_diff(self, current_time, start_time):
        return (current_time - start_time + 10240) % 10240

    def __f_time(self, fn, sfn):
        return fn * 10 + sfn

    def __cmp_queues(self):
        self.mac_buffer = sorted(self.mac_buffer, key=lambda x: x['Packet ID'])
        new_queue = []
        for packet in self.mac_buffer:
            if packet['Transmission Type'] == "New Packet":
                new_queue.append(packet)
        self.mac_buffer = new_queue

    def update_time(self, sysfn, subfn):
        self.fn = sysfn
        self.sfn = subfn
