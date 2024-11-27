
#!/usr/bin/python
# Filename: modified_ul_mac_latency_analyzer.py

"""
Enhanced UL MAC Latency Analyzer with additional metrics for uplink MAC layer latency.

Author: AI Assistant
"""

from mobile_insight.analyzer.analyzer import *

__all__ = ["ModifiedUlMacLatencyAnalyzer"]

class ModifiedUlMacLatencyAnalyzer(Analyzer):

    def __init__(self):
        Analyzer.__init__(self)

        self.add_source_callback(self.__msg_callback)

        # Initialize internal state variables
        self.last_bytes = 0
        self.buffer = {}
        self.ctrl_pkt_sfn = None
        self.cur_fn = 0
        self.lat_stat = []
        self.queue_length = 0
        self.total_sent_packets = 0

    def set_source(self, source):
        """
        Set the trace source and enable specific logs.

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)

        # Enable UL MAC Buffer Status log
        source.enable_log("LTE_MAC_UL_Buffer_Status_Internal")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_MAC_UL_Buffer_Status_Internal":
            log_item = msg.data.decode()

            if 'Subpackets' not in log_item:
                return

            subpackets = log_item['Subpackets']
            for subpkt in subpackets:
                if 'Samples' in subpkt:
                    for sample in subpkt['Samples']:
                        self.cur_fn = sample['sys_fn'] * 10 + sample['sub_fn']
                        if self.ctrl_pkt_sfn is not None:
                            ctrl_pkt_delay = self.cur_fn - self.ctrl_pkt_sfn
                            if ctrl_pkt_delay < 0:
                                ctrl_pkt_delay += 10240
                            self.broadcast_info("UL_CTRL_PKT_DELAY", {
                                "timestamp": log_item['timestamp'],
                                "delay": ctrl_pkt_delay
                            })
                            self.ctrl_pkt_sfn = None

                        for lcid_item in sample['LCIDs']:
                            lcid = lcid_item['LCID']
                            new_bytes = lcid_item['New bytes']
                            ctrl_bytes = lcid_item['Ctrl bytes']
                            total_bytes = new_bytes + ctrl_bytes

                            if total_bytes > 0:
                                if ctrl_bytes > 0:
                                    self.ctrl_pkt_sfn = self.cur_fn

                                if lcid not in self.buffer:
                                    self.buffer[lcid] = []

                                self.buffer[lcid].append({
                                    "timestamp": log_item['timestamp'],
                                    "bytes": total_bytes
                                })

                                self.queue_length += total_bytes
                                self.last_bytes = total_bytes

                        sent_bytes = 0
                        for lcid in self.buffer:
                            for pkt in self.buffer[lcid]:
                                pkt_delay = self.cur_fn - pkt['timestamp']
                                if pkt_delay < 0:
                                    pkt_delay += 10240

                                self.broadcast_info("UL_PKT_DELAY", {
                                    "lcid": lcid,
                                    "timestamp": log_item['timestamp'],
                                    "delay": pkt_delay
                                })
                                sent_bytes += pkt['bytes']

                        self.total_sent_packets += sent_bytes
                        self.broadcast_info("TOTAL_SENT_PACKETS", {
                            "timestamp": log_item['timestamp'],
                            "total_packets": self.total_sent_packets
                        })

                        # Clear buffer after sending
                        self.buffer.clear()
                        self.queue_length = 0
