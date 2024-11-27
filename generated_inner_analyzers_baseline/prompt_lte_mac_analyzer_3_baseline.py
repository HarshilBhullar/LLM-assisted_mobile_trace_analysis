
from mobile_insight.analyzer.analyzer import Analyzer

class ModifiedLteMacAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.grant_received = 0
        self.grant_utilized = 0
        self.buffer_status = {}
        self.harq_processes = {}

    def set_source(self, source):
        self.source = source
        self.source.enable_log("LTE_MAC_UL_Tx_Statistics")
        self.source.enable_log("LTE_MAC_UL_Buffer_Status_Internal")
        self.source.enable_log("LTE_PHY_PDSCH_Stat_Indication")
        self.source.set_callback(self.__msg_callback)

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_MAC_UL_Tx_Statistics":
            self.__process_ul_tx_statistics(msg)
        elif msg.type_id == "LTE_MAC_UL_Buffer_Status_Internal":
            self.__process_ul_buffer_status(msg)
        elif msg.type_id == "LTE_PHY_PDSCH_Stat_Indication":
            self.__process_pdsch_stat(msg)

    def __process_ul_tx_statistics(self, msg):
        # Extract relevant fields for uplink grant analysis
        grants = msg.data.get("Grants", [])
        for grant in grants:
            self.grant_received += grant.get('grant_size', 0)
            self.grant_utilized += grant.get('used_size', 0)

        ul_grant_utilization = (self.grant_utilized / self.grant_received) if self.grant_received > 0 else 0
        self.broadcast_info("UL Grant Utilization", ul_grant_utilization)

    def __process_ul_buffer_status(self, msg):
        # Update buffer status and calculate control packet delays.
        buffer_status = msg.data.get("Buffer Status", {})
        self.buffer_status.update(buffer_status)

        # Calculate and broadcast control packet delays (simplified example)
        control_packet_delays = {k: v for k, v in buffer_status.items()}
        self.broadcast_info("Control Packet Delays", control_packet_delays)

    def __process_pdsch_stat(self, msg):
        # Analyze HARQ processes and retransmissions.
        pdsch_stats = msg.data.get("PDSCH Stats", [])
        for stat in pdsch_stats:
            process_id = stat.get('process_id')
            if process_id not in self.harq_processes:
                self.harq_processes[process_id] = {'retransmissions': 0, 'delay': 0}
            
            harq_info = self.harq_processes[process_id]
            if stat.get('crc_result') == 'FAIL':
                harq_info['retransmissions'] += 1
                harq_info['delay'] += stat.get('transmission_delay', 0)

        retransmission_delays = {k: v['delay'] for k, v in self.harq_processes.items()}
        self.broadcast_info("Retransmission Delays", retransmission_delays)
