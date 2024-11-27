
from mobile_insight.analyzer.analyzer import Analyzer

class ModifiedUlMacLatencyAnalyzer(Analyzer):
    def __init__(self):
        super(ModifiedUlMacLatencyAnalyzer, self).__init__()
        self.last_bytes = 0
        self.buffer = []
        self.ctrl_pkt_sfn = {}
        self.cur_fn = 0
        self.lat_stat = []
        self.queue_length = 0
        self.total_delay = 0

    def set_source(self, source):
        super(ModifiedUlMacLatencyAnalyzer, self).set_source(source)
        source.enable_log("LTE_MAC_UL_Buffer_Status_Internal")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_MAC_UL_Buffer_Status_Internal":
            self.__process_buffer_status(msg)

    def __process_buffer_status(self, msg):
        try:
            log_item = msg.data.decode()
            subpkt = log_item['Subpackets'][0]

            sys_fn = subpkt['Sample']['Sys FN']
            sub_fn = subpkt['Sample']['Sub FN']
            new_bytes = subpkt['Sample']['New Compressed Bytes']
            ctrl_bytes = subpkt['Sample']['Ctrl Compressed Bytes']
            total_bytes = new_bytes + ctrl_bytes

            # Handle system and subframe number rollovers
            if sys_fn < self.cur_fn:
                self.cur_fn = sys_fn + 1024
            else:
                self.cur_fn = sys_fn

            # Update buffer and control packet information
            self.buffer.append((self.cur_fn, sub_fn, total_bytes))
            self.ctrl_pkt_sfn[(sys_fn, sub_fn)] = ctrl_bytes

            # Calculate packet delay
            self.calculate_latency()

        except Exception as e:
            self.log_error("Exception in processing buffer status: " + str(e))

    def calculate_latency(self):
        current_time = self.cur_fn
        packet_delay = 0
        
        # Process each packet in buffer
        for fn, sfn, bytes in self.buffer:
            if (fn, sfn) in self.ctrl_pkt_sfn:
                packet_delay += current_time - fn
                self.total_delay += packet_delay
                self.lat_stat.append(packet_delay)
        
        # Broadcast delay metrics
        self.broadcast_delay_metrics(packet_delay, self.total_delay)

    def broadcast_delay_metrics(self, packet_delay, total_delay):
        self.broadcast_info("Packet Delay: {} ms, Total Delay: {} ms".format(packet_delay, total_delay))

    def set_source(self, source):
        super(ModifiedUlMacLatencyAnalyzer, self).set_source(source)
        source.enable_log("LTE_MAC_UL_Buffer_Status_Internal")
        source.add_callback(self.__msg_callback)
