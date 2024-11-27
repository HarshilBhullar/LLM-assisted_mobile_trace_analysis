
from mobile_insight.analyzer.analyzer import Analyzer

class ModifiedLtePhyAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)
        
        # Initialize counters and data structures
        self.dl_bandwidth = 0
        self.ul_bandwidth = 0
        self.modulation_counter = {'QPSK': 0, '16QAM': 0, '64QAM': 0}
        self.cqi_values = []

    def set_source(self, source):
        Analyzer.set_source(self, source)
        source.enable_log("LTE_PHY_PDSCH_Packet")
        source.enable_log("LTE_PHY_PUCCH_Tx_Report")
        source.enable_log("LTE_PHY_PUSCH_CSF")
        source.enable_log("LTE_PHY_PUSCH_Tx_Report")
        source.enable_log("LTE_MAC_UL_Tx_Statistics")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_PHY_PDSCH_Packet":
            self.callback_pdsch(msg)
        elif msg.type_id == "LTE_PHY_PUCCH_Tx_Report":
            self.callback_pucch(msg)
        elif msg.type_id == "LTE_PHY_PUSCH_CSF":
            self.callback_pusch(msg)
        elif msg.type_id == "LTE_PHY_PUSCH_Tx_Report":
            self.callback_pusch_tx(msg)
        elif msg.type_id == "LTE_MAC_UL_Tx_Statistics":
            self.callback_pusch_grant(msg)

    def callback_pdsch(self, msg):
        # Example processing for PDSCH message
        # Extract and update bandwidth and modulation statistics
        self.dl_bandwidth += msg.get('bandwidth', 0)
        modulation = msg.get('modulation', 'QPSK')
        if modulation in self.modulation_counter:
            self.modulation_counter[modulation] += 1
        self.log_info(f"PDSCH: Updated DL bandwidth to {self.dl_bandwidth} and modulation {modulation} count to {self.modulation_counter[modulation]}.")

    def callback_pucch(self, msg):
        # Example processing for PUCCH message
        # Log PUCCH transmission power
        pucch_power = msg.get('tx_power', 0)
        self.log_info(f"PUCCH: Transmission power is {pucch_power}.")

    def callback_pusch(self, msg):
        # Update CQI values for prediction
        cqi = msg.get('cqi', 0)
        self.cqi_values.append(cqi)
        self.log_info(f"PUSCH: Received CQI {cqi}, current CQI list: {self.cqi_values}.")
        self.predict_bw()

    def callback_pusch_tx(self, msg):
        # Analyze PUSCH transmission power
        pusch_power = msg.get('tx_power', 0)
        self.log_info(f"PUSCH TX: Transmission power is {pusch_power}.")

    def callback_pusch_grant(self, msg):
        # Calculate UL grant utilization
        ul_grant = msg.get('ul_grant', 0)
        self.ul_bandwidth += ul_grant
        self.log_info(f"PUSCH Grant: Updated UL bandwidth to {self.ul_bandwidth}.")

    def predict_bw(self):
        if not self.cqi_values:
            return
        # Example prediction logic using CQI
        avg_cqi = sum(self.cqi_values) / len(self.cqi_values)
        predicted_bw = avg_cqi * 10  # Simplified prediction logic
        self.log_info(f"Predicted downlink bandwidth based on CQI: {predicted_bw}")
