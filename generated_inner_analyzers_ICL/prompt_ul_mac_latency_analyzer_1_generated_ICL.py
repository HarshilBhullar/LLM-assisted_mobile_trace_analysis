
#!/usr/bin/python
# Filename: modified_ul_mac_latency_analyzer.py

"""
Modified UL MAC Latency Analyzer
Author: [Your Name]
"""

from mobile_insight.analyzer.analyzer import *

__all__ = ["ModifiedUlMacLatencyAnalyzer"]

class ModifiedUlMacLatencyAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)

        # Initialize necessary variables
        self.last_bytes = 0
        self.buffer = []
        self.ctrl_pkt_sfn = None
        self.cur_fn = -1
        self.lat_stat = []
        self.queue_length = 0
        self.total_delay = 0

    def set_source(self, source):
        """
        Set the trace source. Enable the necessary logs.

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)
        source.enable_log("LTE_MAC_UL_Buffer_Status_Internal")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_MAC_UL_Buffer_Status_Internal":
            log_item = msg.data.decode()
            for subpkt in log_item['Subpackets']:
                for sample in subpkt['Samples']:
                    sfn = sample['Sub FN']
                    fn = sample['Sys FN']
                    self.__update_time(sfn, fn)

                    total_bytes = 0
                    new_bytes = 0
                    ctrl_bytes = 0

                    if sample['LCIDs']:
                        data = sample['LCIDs'][-1]
                        total_bytes = data['Total Bytes']
                        new_bytes = data['New Compressed Bytes']
                        ctrl_bytes = data['Ctrl bytes']

                    self.__update_buffer(total_bytes, new_bytes, ctrl_bytes, fn, sfn)

    def __update_time(self, sfn, fn):
        if self.cur_fn >= 0:
            self.cur_fn += 1
            if self.cur_fn == 1024:
                self.cur_fn = 0

        if sfn < 10:
            self.cur_fn = fn

    def __update_buffer(self, total_bytes, new_bytes, ctrl_bytes, fn, sfn):
        if total_bytes > self.last_bytes:
            self.buffer.append([total_bytes - self.last_bytes, self.__f_time(fn, sfn), -1])
            self.queue_length += total_bytes - self.last_bytes

        elif total_bytes < self.last_bytes:
            outgoing_buffer = self.last_bytes - total_bytes
            while outgoing_buffer > 0 and self.buffer:
                packet = self.buffer[0]
                if packet[2] == -1:
                    packet[2] = self.__f_time(fn, sfn)

                if packet[0] > outgoing_buffer:
                    packet[0] -= outgoing_buffer
                    break
                else:
                    delay = self.__f_time_diff(packet[1], packet[2])
                    self.lat_stat.append(delay)
                    self.total_delay += delay
                    outgoing_buffer -= packet[0]
                    self.buffer.pop(0)

            self.queue_length -= outgoing_buffer

        self.last_bytes = total_bytes

    def __f_time(self, fn, sfn):
        return fn * 10 + sfn

    def __f_time_diff(self, t1, t2):
        if t1 > t2:
            return t2 + 10240 - t1
        else:
            return t2 - t1 + 1

    def broadcast_metrics(self):
        print(f"Total Delay: {self.total_delay}")
        for delay in self.lat_stat:
            print(f"Packet Delay: {delay}")
