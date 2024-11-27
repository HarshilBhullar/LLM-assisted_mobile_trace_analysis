
from mobile_insight.analyzer.analyzer import Analyzer

class ModifiedUlMacLatencyAnalyzer(Analyzer):
    def __init__(self):
        super().__init__()
        self.last_bytes = 0
        self.buffer = {}
        self.ctrl_pkt_sfn = -1
        self.cur_fn = -1
        self.lat_stat = {}
        self.queue_length = 0
        self.total_sent_packets = 0

    def set_source(self, source):
        super().set_source(source)
        source.enable_log("LTE_MAC_UL_Buffer_Status_Internal")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_MAC_UL_Buffer_Status_Internal":
            log_item = msg.data.decode()

            # Process the log item to update the MAC UL buffer status
            if 'Subpackets' in log_item:
                for subpkt in log_item['Subpackets']:
                    if 'Samples' in subpkt:
                        for sample in subpkt['Samples']:
                            self.cur_fn = sample.get('Sys FN', -1)
                            lcid_data = sample.get('LCIDs', [])

                            total_bytes = 0
                            for lcid in lcid_data:
                                new_bytes = lcid.get('New bytes', 0)
                                ctrl_bytes = lcid.get('Ctrl bytes', 0)
                                total_bytes += new_bytes + ctrl_bytes

                            if self.ctrl_pkt_sfn != -1:
                                ctrl_pkt_delay = self.cur_fn - self.ctrl_pkt_sfn
                                self.broadcast_info('UL_CTRL_PKT_DELAY', {'timestamp': msg.timestamp, 'delay': ctrl_pkt_delay})
                                self.ctrl_pkt_sfn = -1  # Reset control packet SFN

                            sent_bytes = self.last_bytes - total_bytes
                            if sent_bytes > 0:
                                self.total_sent_packets += 1
                                self.lat_stat[self.cur_fn] = {'timestamp': msg.timestamp, 'delay': sent_bytes}
                                self.broadcast_info('UL_PKT_DELAY', {'timestamp': msg.timestamp, 'delay': sent_bytes})

                            self.broadcast_info('TOTAL_SENT_PACKETS', {'total_sent_packets': self.total_sent_packets})
                            self.last_bytes = total_bytes
