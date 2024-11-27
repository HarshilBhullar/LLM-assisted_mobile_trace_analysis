
#!/usr/bin/python
# Filename: ul_mac_latency_analyzer_v2.py
"""
UlMacLatencyAnalyzerV2
Enhances the functionality of UlMacLatencyAnalyzer to monitor and manage uplink latency breakdown with additional metrics

Author: Auto-generated
"""

from mobile_insight.analyzer.analyzer import Analyzer

__all__ = ["UlMacLatencyAnalyzerV2"]

class UlMacLatencyAnalyzerV2(Analyzer):

    def __init__(self):
        Analyzer.__init__(self)

        self.add_source_callback(self.__msg_callback)

        self.last_bytes_in_ul_buffer = 0
        self.buffered_ul_packets = []
        self.control_packet_timestamps = {}
        self.current_sys_fn = -1
        self.total_latency = 0
        self.total_latency_count = 0

    def reset(self):
        self.last_bytes_in_ul_buffer = 0
        self.buffered_ul_packets = []
        self.control_packet_timestamps = {}
        self.current_sys_fn = -1
        self.total_latency = 0
        self.total_latency_count = 0

    def set_source(self, source):
        Analyzer.set_source(self, source)
        source.enable_log("LTE_MAC_UL_Buffer_Status_Internal")

    def __msg_callback(self, msg):
        log_item = msg.data.decode()

        if msg.type_id == "LTE_MAC_UL_Buffer_Status_Internal":
            self.__process_ul_buffer_status(log_item)

    def __process_ul_buffer_status(self, log_item):
        try:
            sys_fn = int(log_item['sys_fn'])
            sub_fn = int(log_item['sub_fn'])
            current_time = log_item['timestamp']

            if self.current_sys_fn != -1 and (sys_fn * 10 + sub_fn) < (self.current_sys_fn * 10):
                self.reset()

            self.current_sys_fn = sys_fn

            total_bytes = int(log_item['total_bytes'])
            new_bytes = int(log_item['new_bytes'])
            control_bytes = int(log_item['control_bytes'])

            if total_bytes < self.last_bytes_in_ul_buffer:
                self.buffered_ul_packets.append({
                    'timestamp': current_time,
                    'new_bytes': new_bytes,
                    'control_bytes': control_bytes
                })

            self.last_bytes_in_ul_buffer = total_bytes

            self.__calculate_latency(current_time)

        except Exception as e:
            self.log_warning(f"Exception processing UL Buffer Status: {e}")
            self.reset()

    def __calculate_latency(self, current_time):
        while self.buffered_ul_packets:
            packet = self.buffered_ul_packets.pop(0)
            latency = (current_time - packet['timestamp']).total_seconds() * 1000  # ms
            self.total_latency += latency
            self.total_latency_count += 1

            self.broadcast_info(f"Packet latency: {latency} ms")

        if self.total_latency_count > 0:
            avg_latency = self.total_latency / self.total_latency_count
            self.broadcast_info(f"Average total latency: {avg_latency} ms")
