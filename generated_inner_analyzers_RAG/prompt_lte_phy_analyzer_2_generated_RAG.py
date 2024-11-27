
#!/usr/bin/python
# Filename: modified_lte_phy_analyzer.py

"""
A modified LTE PHY-layer analyzer with enhanced analysis capabilities.

Author: Your Name
"""

from mobile_insight.analyzer.analyzer import *

__all__ = ["ModifiedLtePhyAnalyzer"]


class ModifiedLtePhyAnalyzer(Analyzer):

    def __init__(self):
        Analyzer.__init__(self)

        self.add_source_callback(self.__msg_callback)

        # Initialize counters and storage for analysis
        self.dl_bandwidth = 0
        self.ul_bandwidth = 0
        self.modulation_schemes = {"QPSK": 0, "16QAM": 0, "64QAM": 0}
        self.cqi_values = []

    def set_source(self, source):
        Analyzer.set_source(self, source)

        # Enable necessary logs
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
        log_item = msg.data.decode()
        for record in log_item.get('Records', []):
            modulation = record.get('MCS Index', "")
            self.modulation_schemes[modulation] += 1
            self.dl_bandwidth += record.get('TB Size', 0)
        self.log_info(f"Updated DL bandwidth: {self.dl_bandwidth}")
        self.broadcast_info("DL_BANDWIDTH", {"bandwidth": self.dl_bandwidth})

    def callback_pucch(self, msg):
        log_item = msg.data.decode()
        for record in log_item.get('Records', []):
            pucch_power = record.get('PUCCH Tx Power', 0)
            self.log_info(f"PUCCH Tx Power: {pucch_power}")
            self.broadcast_info("PUCCH_POWER", {"power": pucch_power})

    def callback_pusch(self, msg):
        log_item = msg.data.decode()
        for record in log_item.get('Records', []):
            cqi = record.get('CQI', 0)
            self.cqi_values.append(cqi)
        self.log_info(f"Updated CQI values: {self.cqi_values}")

    def callback_pusch_tx(self, msg):
        log_item = msg.data.decode()
        for record in log_item.get('Records', []):
            pusch_power = record.get('PUSCH Tx Power', 0)
            self.log_info(f"PUSCH Tx Power: {pusch_power}")
            self.broadcast_info("PUSCH_POWER", {"power": pusch_power})

    def callback_pusch_grant(self, msg):
        log_item = msg.data.decode()
        ul_grant = 0
        for subpkt in log_item.get('Subpackets', []):
            ul_grant += subpkt.get('Sample', {}).get('Grant received', 0)
        self.ul_bandwidth += ul_grant
        self.log_info(f"Updated UL bandwidth: {self.ul_bandwidth}")
        self.broadcast_info("UL_BANDWIDTH", {"bandwidth": self.ul_bandwidth})

    def predict_bw(self):
        if not self.cqi_values:
            return 0
        avg_cqi = sum(self.cqi_values) / len(self.cqi_values)
        predicted_bw = avg_cqi * 10  # Placeholder logic for prediction
        self.broadcast_info("PREDICTED_BW", {"predicted_bw": predicted_bw})
        self.log_info(f"Predicted DL bandwidth: {predicted_bw}")
