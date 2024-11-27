
#!/usr/bin/python
# Filename: modified_ul_mac_latency_analyzer.py
"""
modified_ul_mac_latency_analyzer.py
An enhanced analyzer for uplink MAC layer latency with additional metrics and functionalities.

Author: Zhehui Zhang, Modified by [Your Name]
"""

__all__ = ["ModifiedUlMacLatencyAnalyzer"]

from .analyzer import Analyzer

class ModifiedUlMacLatencyAnalyzer(Analyzer):
    """
    An analyzer to monitor and manage enhanced uplink latency breakdown
    """

    def __init__(self):
        Analyzer.__init__(self)

        self.add_source_callback(self.__msg_callback)
        self.last_bytes = {}
        self.buffer = {}
        self.ctrl_pkt_sfn = {}
        self.cur_fn = None
        self.lat_stat = []
        self.queue_length = 0
        self.total_delay = 0

    def set_source(self, source):
        """
        Set the trace source and enable LTE MAC UL Buffer Status Internal log.

        :param source: the trace source.
        :type source: trace collector
        """
        Analyzer.set_source(self, source)
        source.enable_log("LTE_MAC_UL_Buffer_Status_Internal")

    def __msg_callback(self, msg):
        """
        Callback to process each LTE_MAC_UL_Buffer_Status_Internal message.

        :param msg: the event (message) from the trace collector.
        """
        if msg.type_id == "LTE_MAC_UL_Buffer_Status_Internal":
            log_item = msg.data.decode()
            if 'Subpackets' in log_item:
                for i in range(len(log_item['Subpackets'])):
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

                                if new_bytes > self.last_bytes[idx]:
                                    new_bytes -= self.last_bytes[idx]
                                    self.buffer[idx].append([(self.cur_fn[0], self.cur_fn[1]), new_bytes])

                                if ctrl_bytes > 0:
                                    self.ctrl_pkt_sfn[idx] = (self.cur_fn[0], self.cur_fn[1])
                                else:
                                    if self.ctrl_pkt_sfn[idx]:
                                        ctrl_pkt_delay = self.cur_fn[0] * 10 + self.cur_fn[1] - self.ctrl_pkt_sfn[idx][0] * 10 - self.ctrl_pkt_sfn[idx][1]
                                        ctrl_pkt_delay += 10240 if ctrl_pkt_delay < 0 else 0
                                        self.ctrl_pkt_sfn[idx] = None
                                        self.total_delay += ctrl_pkt_delay
                                        self.log_info(f"{log_item['timestamp']} UL_CTRL_PKT_DELAY: {ctrl_pkt_delay}")
                                        self.broadcast_info("UL_CTRL_PKT_DELAY", {'timestamp': log_item['timestamp'], 'delay': ctrl_pkt_delay})

                                if self.last_bytes[idx] > total_bytes:
                                    sent_bytes = self.last_bytes[idx] - total_bytes
                                    while len(self.buffer[idx]) > 0 and sent_bytes > 0:
                                        pkt = self.buffer[idx][0]
                                        if pkt[1] <= sent_bytes:
                                            pkt_delay = self.cur_fn[0] * 10 + self.cur_fn[1] - pkt[0][0] * 10 - pkt[0][1]
                                            pkt_delay += 10240 if pkt_delay < 0 else 0
                                            self.buffer[idx].pop(0)
                                            sent_bytes -= pkt[1]
                                            self.total_delay += pkt_delay
                                            self.log_info(f"{log_item['timestamp']} UL_PKT_DELAY: {pkt_delay}")
                                            self.broadcast_info("UL_PKT_DELAY", {'timestamp': log_item['timestamp'], 'delay': pkt_delay})
                                        else:
                                            pkt[1] -= sent_bytes
                                self.last_bytes[idx] = total_bytes

                            queue_length = sum(self.last_bytes.values())
                            if queue_length > 0 and queue_length != self.queue_length:
                                self.queue_length = queue_length
                                self.log_info(f"{log_item['timestamp']} UL_QUEUE_LENGTH: {queue_length}")
                                self.broadcast_info("UL_QUEUE_LENGTH", {'timestamp': log_item['timestamp'], 'length': queue_length})

    def get_total_delay(self):
        """
        Get the total accumulated delay.

        :returns: the total delay in the uplink MAC layer
        """
        return self.total_delay
