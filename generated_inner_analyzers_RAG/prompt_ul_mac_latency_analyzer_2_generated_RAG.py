
#!/usr/bin/python
# Filename: ul_mac_latency_analyzer_v2.py
"""
A modified version of the UL MAC Latency Analyzer with enhanced metrics

Author: Assistant
"""

from mobile_insight.analyzer.analyzer import *

__all__ = ["UlMacLatencyAnalyzerV2"]

class UlMacLatencyAnalyzerV2(Analyzer):

    def __init__(self):
        Analyzer.__init__(self)

        self.add_source_callback(self.__msg_callback)
        self.last_bytes = {}
        self.buffer = {}
        self.ctrl_pkt_sfn = {}
        self.cur_fn = None
        self.lat_stat = []
        self.queue_length = 0
        self.total_latency = 0

    def set_source(self, source):
        Analyzer.set_source(self, source)
        source.enable_log("LTE_MAC_UL_Buffer_Status_Internal")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_MAC_UL_Buffer_Status_Internal":
            log_item = msg.data.decode()
            if 'Subpackets' in log_item:
                for i in range(0, len(log_item['Subpackets'])):
                    if 'Samples' in log_item['Subpackets'][i]:
                        for sample in log_item['Subpackets'][i]['Samples']:
                            sub_fn = int(sample['Sub FN'])
                            sys_fn = int(sample['Sys FN'])
                            if not (sys_fn >= 1023 and sub_fn >= 9):
                                if self.cur_fn:
                                    lag = sys_fn * 10 + sub_fn - self.cur_fn[0] * 10 - self.cur_fn[1]
                                    if lag > 2 or -10238 < lag < 0:
                                        self.__reset_latencies()
                                self.cur_fn = [sys_fn, sub_fn]
                            elif self.cur_fn:
                                self.cur_fn[1] += 1
                                if self.cur_fn[1] == 10:
                                    self.cur_fn[1] = 0
                                    self.cur_fn[0] += 1
                                if self.cur_fn[0] == 1024:
                                    self.cur_fn = [0, 0]
                            if not self.cur_fn:
                                break

                            for lcid in sample['LCIDs']:
                                try:
                                    idx = lcid['Ld Id']
                                    new_bytes = int(lcid['New Compressed Bytes'])
                                    ctrl_bytes = int(lcid['Ctrl bytes'])
                                    total_bytes = int(lcid['Total Bytes'])
                                except KeyError:
                                    continue

                                if idx not in self.buffer:
                                    self.buffer[idx] = []
                                if idx not in self.last_bytes:
                                    self.last_bytes[idx] = 0
                                if idx not in self.ctrl_pkt_sfn:
                                    self.ctrl_pkt_sfn[idx] = None

                                if not new_bytes == 0:
                                    if new_bytes > self.last_bytes[idx]:
                                        new_bytes = new_bytes - self.last_bytes[idx]
                                        self.buffer[idx].append([(self.cur_fn[0], self.cur_fn[1]), new_bytes])

                                if not ctrl_bytes == 0:
                                    total_bytes -= 2
                                    if not self.ctrl_pkt_sfn[idx]:
                                        self.ctrl_pkt_sfn[idx] = (self.cur_fn[0], self.cur_fn[1])
                                else:
                                    if self.ctrl_pkt_sfn[idx]:
                                        ctrl_pkt_delay = self.__calculate_delay(self.ctrl_pkt_sfn[idx], self.cur_fn)
                                        self.total_latency += ctrl_pkt_delay
                                        self.ctrl_pkt_sfn[idx] = None
                                        self.__broadcast_latency("UL_CTRL_PKT_DELAY", log_item['timestamp'], ctrl_pkt_delay)

                                if self.last_bytes[idx] > total_bytes:
                                    sent_bytes = self.last_bytes[idx] - total_bytes
                                    while len(self.buffer[idx]) > 0 and sent_bytes > 0:
                                        pkt = self.buffer[idx][0]
                                        if pkt[1] <= sent_bytes:
                                            pkt_delay = self.__calculate_delay(pkt[0], self.cur_fn)
                                            self.total_latency += pkt_delay
                                            self.buffer[idx].pop(0)
                                            sent_bytes -= pkt[1]
                                            self.__broadcast_latency("UL_PKT_DELAY", log_item['timestamp'], pkt_delay)
                                        else:
                                            pkt[1] -= sent_bytes
                                self.last_bytes[idx] = total_bytes
                            self.__update_queue_length(log_item['timestamp'])
    
    def __calculate_delay(self, start_fn, end_fn):
        delay = end_fn[0] * 10 + end_fn[1] - start_fn[0] * 10 - start_fn[1]
        delay += 10240 if delay < 0 else 0
        delay += 1  # Extra ms for calculation
        return delay

    def __broadcast_latency(self, event_type, timestamp, delay):
        bcast_dict = {}
        bcast_dict['timestamp'] = timestamp
        bcast_dict['delay'] = delay
        bcast_dict['total_latency'] = self.total_latency
        self.broadcast_info(event_type, bcast_dict)
        self.log_info(f"{timestamp} {event_type}: {delay} ms, Total Latency: {self.total_latency} ms")

    def __update_queue_length(self, timestamp):
        queue_length = 0
        for idx in self.last_bytes:
            queue_length += self.last_bytes[idx]
        if queue_length > 0 and queue_length != self.queue_length:
            self.queue_length = queue_length
            self.log_info(f"{timestamp} UL_QUEUE_LENGTH: {queue_length}")
            bcast_dict = {}
            bcast_dict['timestamp'] = timestamp
            bcast_dict['length'] = queue_length
            self.broadcast_info("UL_QUEUE_LENGTH", bcast_dict)

    def __reset_latencies(self):
        self.last_bytes = {}
        self.buffer = {}
        self.ctrl_pkt_sfn = {}
        self.total_latency = 0
