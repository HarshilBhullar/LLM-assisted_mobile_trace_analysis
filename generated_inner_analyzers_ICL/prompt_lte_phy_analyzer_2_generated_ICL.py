
#!/usr/bin/python
# Filename: modified_lte_phy_analyzer.py
"""
A modified LTE PHY-layer analyzer for advanced analysis.

Author: Yuanjie Li
Modified by: Assistant
"""

from mobile_insight.analyzer.analyzer import *
import numpy as np

__all__ = ["ModifiedLtePhyAnalyzer"]

class ModifiedLtePhyAnalyzer(Analyzer):

    def __init__(self):
        Analyzer.__init__(self)

        self.add_source_callback(self.__msg_callback)

        # Initialize counters and storage for analysis
        self.dl_bandwidth = 0
        self.ul_bandwidth = 0
        self.modulation_stats = {'QPSK': 0, '16QAM': 0, '64QAM': 0}
        self.cqi_values = []
        
        # Pre-trained CQI to bandwidth mapping (example values)
        self.cqi_to_bw_map = {1: 1.4, 2: 3, 3: 5, 4: 10, 5: 15, 6: 20}

    def set_source(self, source):
        """
        Set the trace source. Enable the LTE PHY-layer messages.

        :param source: the trace source.
        """
        Analyzer.set_source(self, source)

        # Enable specific PHY-layer logs
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
        mod_scheme = log_item.get("Modulation", None)
        if mod_scheme in self.modulation_stats:
            self.modulation_stats[mod_scheme] += 1

        dl_bw = log_item.get("DL Bandwidth", 0)
        self.dl_bandwidth = dl_bw
        self.broadcast_info("DL_BANDWIDTH", {"dl_bandwidth": dl_bw})
        self.log_info(f"PDSCH: DL Bandwidth = {dl_bw}, Modulation = {mod_scheme}")

    def callback_pucch(self, msg):
        log_item = msg.data.decode()
        pucch_power = log_item.get("PUCCH Power", None)
        sr_detected = log_item.get("SR", False)
        self.log_info(f"PUCCH: Power = {pucch_power}, Scheduling Request = {sr_detected}")
        self.broadcast_info("PUCCH_TX_POWER", {"pucch_power": pucch_power, "sr_detected": sr_detected})

    def callback_pusch(self, msg):
        log_item = msg.data.decode()
        cqi_value = log_item.get("CQI", None)
        if cqi_value:
            self.cqi_values.append(cqi_value)
            self.predict_bw(cqi_value)
            self.log_info(f"PUSCH: CQI = {cqi_value}")

    def callback_pusch_tx(self, msg):
        log_item = msg.data.decode()
        pusch_power = log_item.get("PUSCH Power", None)
        self.broadcast_info("PUSCH_TX_POWER", {"pusch_power": pusch_power})
        self.log_info(f"PUSCH: TX Power = {pusch_power}")

    def callback_pusch_grant(self, msg):
        log_item = msg.data.decode()
        ul_grant = log_item.get("UL Grant", None)
        self.ul_bandwidth = ul_grant
        self.broadcast_info("UL_BANDWIDTH", {"ul_bandwidth": ul_grant})
        self.log_info(f"UL Grant Utilization: {ul_grant}")

    def predict_bw(self, cqi):
        predicted_bw = self.cqi_to_bw_map.get(cqi, 0)
        self.broadcast_info("PREDICTED_BW", {"predicted_dl_bw": predicted_bw})
        self.log_info(f"Predicted DL Bandwidth based on CQI {cqi} = {predicted_bw}")
