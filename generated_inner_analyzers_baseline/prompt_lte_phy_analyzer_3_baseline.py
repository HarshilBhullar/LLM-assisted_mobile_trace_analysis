
from mobile_insight.analyzer.analyzer import Analyzer

class LtePhyAnalyzerModified(Analyzer):
    def __init__(self):
        super(LtePhyAnalyzerModified, self).__init__()
        self.modulation_count = {'QPSK': 0, '16QAM': 0, '64QAM': 0}
        self.cqi_values = []
        self.uplink_bandwidth = 0
        self.sr_events = 0
        self.pusch_tx_power = []

    def set_source(self, source):
        """
        Set the trace source. Enable the LTE PHY logs needed for analysis.
        
        :param source: the trace source
        """
        super(LtePhyAnalyzerModified, self).set_source(source)
        source.enable_log("LTE_PHY_PDSCH_Packet")
        source.enable_log("LTE_PHY_PUSCH_CSF")
        source.enable_log("LTE_PHY_UL_Tx_Statistics")
        source.enable_log("LTE_PHY_PUCCH_Tx_Report")
        source.enable_log("LTE_PHY_PUSCH_Tx_Report")
        
    def callback_pdsch(self, msg):
        """
        Process PDSCH packets to compute downlink bandwidth and modulation schemes.
        
        :param msg: the message to process
        """
        # Example processing of PDSCH packet
        modulation = msg.get("modulation")
        if modulation in self.modulation_count:
            self.modulation_count[modulation] += 1
        self.broadcast_info("PDSCH", self.modulation_count)

    def callback_pusch(self, msg):
        """
        Handle PUSCH CSF packets to update CQI values.
        
        :param msg: the message to process
        """
        cqi = msg.get("cqi")
        if cqi is not None:
            self.cqi_values.append(cqi)
        self.broadcast_info("PUSCH_CSF", {"CQI": self.cqi_values})

    def callback_pusch_grant(self, msg):
        """
        Process UL Tx Statistics to calculate uplink bandwidth and grant utilization.
        
        :param msg: the message to process
        """
        bandwidth = msg.get("bandwidth")
        if bandwidth is not None:
            self.uplink_bandwidth = bandwidth
        self.broadcast_info("UL_Tx_Statistics", {"Uplink Bandwidth": self.uplink_bandwidth})

    def callback_pucch(self, msg):
        """
        Capture and log PUCCH scheduling requests.
        
        :param msg: the message to process
        """
        sr_event = msg.get("scheduling_request")
        if sr_event:
            self.sr_events += 1
        self.broadcast_info("PUCCH_Tx_Report", {"Scheduling Requests": self.sr_events})

    def callback_pusch_tx(self, msg):
        """
        Extract and log PUSCH transmission power details.
        
        :param msg: the message to process
        """
        tx_power = msg.get("tx_power")
        if tx_power is not None:
            self.pusch_tx_power.append(tx_power)
        self.broadcast_info("PUSCH_Tx_Report", {"Tx Power": self.pusch_tx_power})

    def predict_bw_modified(self):
        """
        Predict downlink bandwidth based on the current CQI values.
        """
        if not self.cqi_values:
            return 0
        average_cqi = sum(self.cqi_values) / len(self.cqi_values)
        # Simplified CQI-to-bandwidth mapping
        predicted_bw = average_cqi * 10
        self.broadcast_info("Predicted_Bandwidth", {"Predicted BW": predicted_bw})
        return predicted_bw

    def __msg_callback(self, msg):
        """
        Determine the type of incoming message and invoke the appropriate handler function.
        
        :param msg: the message to handle
        """
        if msg.type_id == "LTE_PHY_PDSCH_Packet":
            self.callback_pdsch(msg)
        elif msg.type_id == "LTE_PHY_PUSCH_CSF":
            self.callback_pusch(msg)
        elif msg.type_id == "LTE_PHY_UL_Tx_Statistics":
            self.callback_pusch_grant(msg)
        elif msg.type_id == "LTE_PHY_PUCCH_Tx_Report":
            self.callback_pucch(msg)
        elif msg.type_id == "LTE_PHY_PUSCH_Tx_Report":
            self.callback_pusch_tx(msg)
