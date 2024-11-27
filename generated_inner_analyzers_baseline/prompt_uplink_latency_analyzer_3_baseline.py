
from mobile_insight.analyzer.analyzer import Analyzer
import datetime

class UplinkLatencyAnalyzerModified(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)

        # Initialize metrics
        self.cum_err_block = [0]  # Cumulative erroneous blocks
        self.cum_block = [0]      # Cumulative blocks
        self.all_packets = []     # List of all packet latency records

        # Queues to track packet buffering and transmission
        self.buffer_queue = []
        self.transmission_queue = []

        # Enable specific message types for uplink latency analysis
        self.add_source_callback(self.__msg_callback)

    def set_source(self, source):
        super(UplinkLatencyAnalyzerModified, self).set_source(source)
        self.enable_log("LTE_PHY_PUSCH_Tx_Report")
        self.enable_log("LTE_MAC_UL_Buffer_Status_Internal")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_PHY_PUSCH_Tx_Report":
            self._process_pusch_tx_report(msg)
        elif msg.type_id == "LTE_MAC_UL_Buffer_Status_Internal":
            self._process_ul_buffer_status(msg)

    def _process_pusch_tx_report(self, msg):
        # Parse transmission records and update cumulative blocks and erroneous blocks
        try:
            records = msg.data.get('Records', [])
            for record in records:
                if record.get('ReTx', 0) > 0:
                    self.cum_err_block[0] += 1
                self.cum_block[0] += 1

                # Compute modified latency metrics
                tx_latency = self._compute_latency(record)
                self.all_packets.append(tx_latency)
        except Exception as e:
            self.log_warning(f"Error processing PUSCH Tx Report: {e}")

    def _process_ul_buffer_status(self, msg):
        try:
            # Manage packet queue operations and calculate latencies
            current_fn = msg.data.get('FrameNum', -1)
            current_sfn = msg.data.get('SubframeNum', -1)
            buffer_size = msg.data.get('UL_Buffer_Size', 0)

            # Update buffer and transmission queue based on buffer size changes
            self._update_queues(current_fn, current_sfn, buffer_size)
        except Exception as e:
            self.log_warning(f"Error processing UL Buffer Status: {e}")

    def _compute_latency(self, record):
        # Helper function to compute latency from transmission records
        waiting_latency = self._compute_waiting_latency(record)
        tx_latency = record.get('Tx Time', 0)  # Example field
        retx_latency = record.get('ReTx Time', 0)  # Example field

        return {
            "Waiting Latency": waiting_latency,
            "Tx Latency": tx_latency,
            "Retx Latency": retx_latency
        }

    def _compute_waiting_latency(self, record):
        # Example utility function to compute time differences
        arrival_time = record.get('Arrival Time', datetime.datetime.now())
        tx_time = record.get('Tx Time', datetime.datetime.now())
        waiting_latency = (tx_time - arrival_time).total_seconds() * 1000  # Convert to ms
        return waiting_latency

    def _update_queues(self, current_fn, current_sfn, buffer_size):
        # Example logic to update queues based on buffer size
        if buffer_size > 0:
            self.buffer_queue.append((current_fn, current_sfn, buffer_size))
        else:
            if self.buffer_queue:
                self.transmission_queue.append(self.buffer_queue.pop(0))
