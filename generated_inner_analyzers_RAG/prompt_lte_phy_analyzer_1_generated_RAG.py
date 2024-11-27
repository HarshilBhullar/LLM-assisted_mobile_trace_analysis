
#!/usr/bin/python
# Filename: lte_phy_analyzer_modified.py
"""
A modified 4G PHY analyzer providing enhanced bandwidth prediction and modulation statistics.

Author: [Your Name]
"""

from mobile_insight.analyzer.analyzer import *

__all__ = ["LtePhyAnalyzerModified"]

class LtePhyAnalyzerModified(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)

        # Initialize counters and variables for PHY layer metrics
        self.dl_bandwidth_stats = {}
        self.ul_bandwidth_stats = {}
        self.modulation_stats = {}
        self.cqi_values = {}

        # Pre-defined CQI to Bandwidth mapping (example values)
        self.cqi_to_bw_mapping = {
            0: 6.0, 1: 6.0, 2: 15.0, 3: 25.0, 4: 36.0,
            5: 48.0, 6: 60.0, 7: 75.0, 8: 90.0, 9: 105.0,
            10: 120.0, 11: 135.0, 12: 150.0, 13: 165.0, 14: 180.0,
            15: 200.0
        }

    def set_source(self, source):
        Analyzer.set_source(self, source)

        # Enable specific LTE PHY layer logs
        source.enable_log("LTE_PHY_PDSCH_Packet")
        source.enable_log("LTE_PHY_PUSCH_CSF")
        source.enable_log("LTE_MAC_UL_Tx_Statistics")
        source.enable_log("LTE_PHY_PUCCH_Tx_Report")
        source.enable_log("LTE_PHY_PUSCH_Tx_Report")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_PHY_PDSCH_Packet":
            self.process_pdsch(msg)
        elif msg.type_id == "LTE_PHY_PUSCH_CSF":
            self.process_pusch_csf(msg)
        elif msg.type_id == "LTE_MAC_UL_Tx_Statistics":
            self.process_ul_tx_statistics(msg)
        elif msg.type_id == "LTE_PHY_PUCCH_Tx_Report":
            self.process_pucch_tx_report(msg)
        elif msg.type_id == "LTE_PHY_PUSCH_Tx_Report":
            self.process_pusch_tx_report(msg)

    def process_pdsch(self, msg):
        log_item = msg.data.decode()
        # Example: Process downlink bandwidth and modulation statistics
        cqi = log_item.get("CQI", None)
        if cqi is not None:
            self.cqi_values['downlink'] = cqi
            predicted_bw = self.predict_bw(cqi)
            self.log_info(f"Predicted Downlink Bandwidth: {predicted_bw} Mbps")
            self.broadcast_info('Predicted_DL_BW', {'cqi': cqi, 'bw': predicted_bw})

    def process_pusch_csf(self, msg):
        log_item = msg.data.decode()
        # Example: Capture and log CQI values for uplink
        cqi = log_item.get("CQI", None)
        if cqi is not None:
            self.cqi_values['uplink'] = cqi
            self.log_info(f"Uplink CQI: {cqi}")

    def process_ul_tx_statistics(self, msg):
        log_item = msg.data.decode()
        # Example: Determine uplink grant utilization and calculate bandwidth
        ul_grant = log_item.get("UL Grant", None)
        if ul_grant is not None:
            self.ul_bandwidth_stats['grant'] = ul_grant
            self.log_info(f"Uplink Grant: {ul_grant}")

    def process_pucch_tx_report(self, msg):
        log_item = msg.data.decode()
        # Example: Analyze and log PUCCH scheduling requests
        sr = log_item.get("SR", None)
        if sr is not None:
            self.log_info(f"PUCCH Scheduling Request: {sr}")

    def process_pusch_tx_report(self, msg):
        log_item = msg.data.decode()
        # Example: Log power measurements related to PUSCH transmissions
        power = log_item.get("Power", None)
        if power is not None:
            self.log_info(f"PUSCH Transmission Power: {power}")

    def predict_bw(self, cqi):
        # Predict bandwidth based on CQI value
        return self.cqi_to_bw_mapping.get(cqi, 0)
