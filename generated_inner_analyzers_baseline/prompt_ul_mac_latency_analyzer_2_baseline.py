
from mobile_insight.analyzer.analyzer import Analyzer
from mobile_insight.analyzer import UlMacLatencyAnalyzer

class UlMacLatencyAnalyzerV2(Analyzer):
    def __init__(self):
        super(UlMacLatencyAnalyzerV2, self).__init__()
        self.add_source_callback(self.__msg_callback)
        
        # Initialize data structures for tracking metrics
        self.last_mac_ul_bytes = 0
        self.buffered_packets = {}
        self.control_packet_timestamps = {}
        self.current_sfn = -1
        self.total_latency = 0

    def set_source(self, source):
        """
        Set the trace source. Enable necessary logs.
        """
        super(UlMacLatencyAnalyzerV2, self).set_source(source)
        source.enable_log("LTE_MAC_UL_Buffer_Status_Internal")

    def __msg_callback(self, msg):
        """
        Callback function to process incoming messages and update latency stats.
        """
        if msg.type_id == "LTE_MAC_UL_Buffer_Status_Internal":
            log_item = msg.data.decode()

            # Process log and update MAC UL buffer status
            for sample in log_item.get("Samples", []):
                self.current_sfn = sample.get("System Frame Number", -1)
                
                if self.current_sfn == -1 or self.current_sfn < 0 or self.current_sfn > 1023:
                    # Handle invalid system frame number
                    continue

                # Extract relevant data
                new_bytes = sample.get("New Bytes", 0)
                control_bytes = sample.get("Control Bytes", 0)
                total_bytes = sample.get("Total Bytes", 0)

                # Calculate and update latencies
                self.__update_packet_statistics(new_bytes, control_bytes, total_bytes)

    def __update_packet_statistics(self, new_bytes, control_bytes, total_bytes):
        """
        Helper function to calculate latency and update statistics.
        """
        # Manage buffered packets
        if new_bytes > 0:
            # Record new packet with current timestamp
            self.buffered_packets[self.current_sfn] = new_bytes

        if control_bytes > 0:
            # Calculate latency for control packets
            if self.current_sfn in self.buffered_packets:
                latency = self.current_sfn - self.control_packet_timestamps.get(self.current_sfn, self.current_sfn)
                self.total_latency += latency
                # Broadcast or log the calculated latency
                self.broadcast_info("Control Packet Latency: {} frames".format(latency))

        # Update control packet timestamps
        self.control_packet_timestamps[self.current_sfn] = self.current_sfn

        # Calculate latency for data packets
        if total_bytes > 0:
            for sfn, bytes in list(self.buffered_packets.items()):
                if bytes <= total_bytes:
                    latency = self.current_sfn - sfn
                    self.total_latency += latency
                    # Broadcast or log the calculated latency
                    self.broadcast_info("Data Packet Latency: {} frames".format(latency))
                    total_bytes -= bytes
                    del self.buffered_packets[sfn]
                else:
                    self.buffered_packets[sfn] -= total_bytes
                    break

        # Reset if there's a time lag or invalid state
        if abs(self.current_sfn - max(self.control_packet_timestamps.values(), default=self.current_sfn)) > 10:
            self.__reset_statistics()

    def __reset_statistics(self):
        """
        Reset statistics and buffered data due to invalid state.
        """
        self.last_mac_ul_bytes = 0
        self.buffered_packets.clear()
        self.control_packet_timestamps.clear()
        self.total_latency = 0
        self.current_sfn = -1

    def broadcast_info(self, message):
        """
        Utility function for broadcasting latency information.
        """
        print(message)
