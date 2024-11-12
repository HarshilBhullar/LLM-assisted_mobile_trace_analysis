
#!/usr/bin/python
# Filename: lte_phy_analyzer_modified.py

"""
A modified LTE PHY analyzer with enhanced bandwidth prediction and modulation statistics.
Author: AI Assistant
"""

from mobile_insight.analyzer.analyzer import Analyzer
import logging

__all__ = ["LtePhyAnalyzerModified"]

class LtePhyAnalyzerModified(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.dl_bandwidth = 0
        self.ul_bandwidth = 0
        self.cqi_values = []
        self.dl_modulation_stats = {}
        self.ul_modulation_stats = {}
        self.cqi_bw_mapping = {  # Example mapping, adjust as needed
            0: 0.0, 1: 0.1, 2: 0.2, 3: 0.3,
            4: 0.4, 5: 0.5, 6: 0.6, 7: 0.7,
            8: 0.8, 9: 0.9, 10: 1.0, 11: 1.1,
            12: 1.2, 13: 1.3, 14: 1.4, 15: 1.5
        }
        self.add_source_callback(self.__msg_callback)

    def set_source(self, source):
        Analyzer.set_source(self, source)
        source.enable_log("LTE_PHY_PDSCH_Packet")
        source.enable_log("LTE_PHY_PUSCH_CSF")
        source.enable_log("LTE_MAC_UL_Tx_Statistics")
        source.enable_log("LTE_PHY_PUCCH_Tx_Report")
        source.enable_log("LTE_PHY_PUSCH_Tx_Report")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_PHY_PDSCH_Packet":
            self.__process_pdsch_packet(msg)
        elif msg.type_id == "LTE_PHY_PUSCH_CSF":
            self.__process_pusch_csf(msg)
        elif msg.type_id == "LTE_MAC_UL_Tx_Statistics":
            self.__process_ul_tx_statistics(msg)
        elif msg.type_id == "LTE_PHY_PUCCH_Tx_Report":
            self.__process_pucch_tx_report(msg)
        elif msg.type_id == "LTE_PHY_PUSCH_Tx_Report":
            self.__process_pusch_tx_report(msg)

    def __process_pdsch_packet(self, msg):
        log_item = msg.data.decode()
        if "CQI" in log_item:
            self.cqi_values.append(log_item["CQI"])
        if "Modulation" in log_item:
            modulation = log_item["Modulation"]
            if modulation in self.dl_modulation_stats:
                self.dl_modulation_stats[modulation] += 1
            else:
                self.dl_modulation_stats[modulation] = 1
        self.predict_bw()

    def __process_pusch_csf(self, msg):
        log_item = msg.data.decode()
        if "CQI" in log_item:
            self.cqi_values.append(log_item["CQI"])

    def __process_ul_tx_statistics(self, msg):
        log_item = msg.data.decode()
        if "Uplink Grant" in log_item:
            self.ul_bandwidth += log_item["Uplink Grant"]

    def __process_pucch_tx_report(self, msg):
        log_item = msg.data.decode()
        # Process PUCCH Tx Report if needed

    def __process_pusch_tx_report(self, msg):
        log_item = msg.data.decode()
        # Process PUSCH Tx Report if needed

    def predict_bw(self):
        if self.cqi_values:
            avg_cqi = sum(self.cqi_values) / len(self.cqi_values)
            predicted_bw = self.cqi_bw_mapping.get(int(avg_cqi), 0)
            logging.info(f"Predicted Downlink Bandwidth: {predicted_bw}")
            self.broadcast_info("PREDICTED_BW", {"predicted_bw": predicted_bw})
