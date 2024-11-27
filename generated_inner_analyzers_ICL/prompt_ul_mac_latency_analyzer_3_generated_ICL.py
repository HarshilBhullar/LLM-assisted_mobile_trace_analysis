
#!/usr/bin/python
# Filename: modified_ul_mac_latency_analyzer.py
"""
modified_ul_mac_latency_analyzer.py
An analyzer to monitor mac layer waiting and processing latency with modified calculations.

Author: [Your Name]
"""

__all__ = ["ModifiedUlMacLatencyAnalyzer"]

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from .analyzer import *

class ModifiedUlMacLatencyAnalyzer(Analyzer):
    """
    An analyzer to monitor and manage uplink latency breakdown with additional metrics.
    """
    def __init__(self):
        Analyzer.__init__(self)

        self.add_source_callback(self.__msg_callback)
        self.last_bytes = {} # LCID -> bytes <int> Last remaining bytes in MAC UL buffer
        self.buffer = {} # LCID -> [(sys_fn, sub_fn), packet_bytes] buffered mac ul packets
        self.ctrl_pkt_sfn = {} # LCID -> [sys_fn, sub_fn] when last mac ul control packet comes
        self.cur_fn = None # Record current [sys_fn, sub_fn] for mac ul buffer
        self.lat_stat = [] # Record ul waiting latency (ts, sys_fn, sub_fn, pdu_size)
        self.queue_length = 0
        self.total_sent_packets = 0 # New metric: total packets sent

    def set_source(self, source):
        """
        Set the trace source. Enable the cellular signaling messages.

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)

        # Phy-layer logs
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
                                        self.last_bytes = {}
                                        self.buffer = {}
                                        self.ctrl_pkt_sfn = {}
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
                                idx = lcid['Ld Id']
                                new_bytes = int(lcid.get('New Compressed Bytes', lcid.get('New bytes', 0)))
                                ctrl_bytes = int(lcid.get('Ctrl bytes', 0))
                                total_bytes = new_bytes + ctrl_bytes if 'Total Bytes' not in lcid else int(lcid['Total Bytes'])

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
                                        ctrl_pkt_delay = self.cur_fn[0] * 10 + self.cur_fn[1] \
                                                         - self.ctrl_pkt_sfn[idx][0] * 10 - self.ctrl_pkt_sfn[idx][1]
                                        ctrl_pkt_delay += 10240 if ctrl_pkt_delay < 0 else 0
                                        self.ctrl_pkt_sfn[idx] = None
                                        bcast_dict = {}
                                        bcast_dict['timestamp'] = str(log_item['timestamp'])
                                        bcast_dict['delay'] = str(ctrl_pkt_delay)
                                        self.broadcast_info("UL_CTRL_PKT_DELAY", bcast_dict)

                                if self.last_bytes[idx] > total_bytes:
                                    sent_bytes = self.last_bytes[idx] - total_bytes
                                    while len(self.buffer[idx]) > 0 and sent_bytes > 0:
                                        pkt = self.buffer[idx][0]
                                        if pkt[1] <= sent_bytes:
                                            pkt_delay = self.cur_fn[0] * 10 + self.cur_fn[1] \
                                                             - pkt[0][0] * 10 - pkt[0][1]
                                            pkt_delay += 10240 if pkt_delay < 0 else 0
                                            self.buffer[idx].pop(0)
                                            sent_bytes -= pkt[1]
                                            self.lat_stat.append((log_item['timestamp'], \
                                                                 self.cur_fn[0], self.cur_fn[1], pkt[1], pkt_delay))
                                            self.total_sent_packets += 1 # Increase sent packets count
                                            bcast_dict = {}
                                            bcast_dict['timestamp'] = str(log_item['timestamp'])
                                            bcast_dict['delay'] = str(pkt_delay)
                                            self.broadcast_info("UL_PKT_DELAY", bcast_dict)
                                        else:
                                            pkt[1] -= sent_bytes
                                self.last_bytes[idx] = total_bytes

                            self.queue_length = sum(self.last_bytes.values()) 

                            # Broadcast total sent packets count
                            bcast_dict = {'total_sent_packets': self.total_sent_packets}
                            self.broadcast_info("TOTAL_SENT_PACKETS", bcast_dict)
