
from mobile_insight.analyzer.analyzer import *

class UplinkLatencyAnalyzerModified(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.cum_err_block = 0
        self.cum_block = 0
        self.cum_retx_latency = 0
        self.all_packets = []
        self.packet_queue = []

    def set_source(self, source):
        Analyzer.set_source(self, source)
        source.enable_log("LTE_PHY_PUSCH_Tx_Report")
        source.enable_log("LTE_MAC_UL_Buffer_Status_Internal")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_PHY_PUSCH_Tx_Report":
            self._process_pusch_report(msg)
        elif msg.type_id == "LTE_MAC_UL_Buffer_Status_Internal":
            self._process_ul_buffer_status(msg)

    def _process_pusch_report(self, msg):
        # Extract and process the PUSCH Tx report
        for record in msg.data.get('Records', []):
            self.cum_block += 1
            if record.get('Error'):
                self.cum_err_block += 1
                retx_latency = record.get('Retx Latency', 0)
                self.cum_retx_latency += retx_latency

    def _process_ul_buffer_status(self, msg):
        # Process UL buffer status to manage packet queue
        for buffer in msg.data.get('Buffers', []):
            packet = {
                'Waiting Latency': buffer.get('Waiting Latency', 0),
                'Tx Latency': buffer.get('Tx Latency', 0),
                'Retx Latency': buffer.get('Retx Latency', 0)
            }
            self.packet_queue.append(packet)

        self._update_packet_statistics()

    def _update_packet_statistics(self):
        while self.packet_queue:
            packet = self.packet_queue.pop(0)
            self.all_packets.append(packet)

    def calculate_time_difference(self, start_time, end_time):
        # Helper function to compute time difference
        return end_time - start_time

    def get_statistics(self):
        return {
            'cumulative_error_blocks': self.cum_err_block,
            'cumulative_blocks': self.cum_block,
            'cumulative_retx_latency': self.cum_retx_latency,
            'all_packets': self.all_packets
        }
