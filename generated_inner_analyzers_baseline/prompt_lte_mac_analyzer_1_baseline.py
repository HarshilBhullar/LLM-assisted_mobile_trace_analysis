
from mobile_insight.analyzer.analyzer import Analyzer

class LteMacAnalyzerModified(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.ul_grant_utilization = []
        self.mac_retransmissions = 0
        self.rlc_retransmissions = 0

    def set_source(self, source):
        Analyzer.set_source(self, source)
        self.source.enable_log("LTE_MAC_UL_Tx_Statistics")
        self.source.enable_log("LTE_MAC_UL_Buffer_Status_Internal")
        self.source.enable_log("LTE_PHY_PDSCH_Stat_Indication")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_MAC_UL_Tx_Statistics":
            self._process_ul_tx_statistics(msg)
        elif msg.type_id == "LTE_MAC_UL_Buffer_Status_Internal":
            self._process_ul_buffer_status(msg)
        elif msg.type_id == "LTE_PHY_PDSCH_Stat_Indication":
            self._process_pdsch_stat_indication(msg)

    def _process_ul_tx_statistics(self, msg):
        # Extract UL grant utilization data
        grant_util = msg.data.get("Grant Utilization", 0)
        self.ul_grant_utilization.append(grant_util)

        # Calculate variance of UL grant utilization
        if len(self.ul_grant_utilization) > 1:
            mean_util = sum(self.ul_grant_utilization) / len(self.ul_grant_utilization)
            variance = sum((x - mean_util) ** 2 for x in self.ul_grant_utilization) / len(self.ul_grant_utilization)
            self.log_info(f"UL Grant Utilization Variance: {variance}")

    def _process_ul_buffer_status(self, msg):
        # Analyze buffer status and manage packet delays
        buffer_status = msg.data.get("Buffer Status", {})
        delay = buffer_status.get("Packet Delay", 0)
        self.log_info(f"Packet Delay: {delay}")

    def _process_pdsch_stat_indication(self, msg):
        # Track HARQ and MAC retransmissions
        harq_failures = msg.data.get("HARQ Failures", 0)
        self.mac_retransmissions += harq_failures
        self.log_info(f"HARQ Failures: {harq_failures}")

    def run(self):
        # This method is called during execution to start processing
        self.set_callback(self.__msg_callback)

    def log_info(self, msg):
        # Custom method to log information
        print(msg)
