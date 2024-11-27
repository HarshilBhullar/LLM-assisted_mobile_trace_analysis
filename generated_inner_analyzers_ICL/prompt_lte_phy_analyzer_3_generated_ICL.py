
#!/usr/bin/python
# Filename: lte_phy_analyzer_modified.py
"""
lte_phy_analyzer_modified.py
Enhanced analysis for LTE PHY layer logs with adjusted metrics

Author: Adapted for demonstration
"""

from mobile_insight.analyzer.analyzer import *
import xml.etree.ElementTree as ET

__all__ = ["LtePhyAnalyzerModified"]

class LtePhyAnalyzerModified(Analyzer):
    """
    A modified analyzer for LTE PHY layer logs
    """

    def __init__(self):
        Analyzer.__init__(self)
        self.cqi_values = []
        self.modulation_counts = {'QPSK': 0, '16QAM': 0, '64QAM': 0}
        self.add_source_callback(self.__msg_callback)

    def set_source(self, source):
        """
        Set the trace source. Enable the LTE PHY layer logs

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)

        # Enable PHY-layer logs
        source.enable_log("LTE_PHY_PDSCH_Stat_Indication")
        source.enable_log("LTE_PHY_PUSCH_CSF")
        source.enable_log("LTE_PHY_UL_Transport_Block")
        source.enable_log("LTE_PHY_PUCCH_Tx_Report")
        source.enable_log("LTE_PHY_PUSCH_Tx_Report")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_PHY_PDSCH_Stat_Indication":
            self.callback_pdsch(msg)
        elif msg.type_id == "LTE_PHY_PUSCH_CSF":
            self.callback_pusch(msg)
        elif msg.type_id == "LTE_PHY_UL_Transport_Block":
            self.callback_pusch_grant(msg)
        elif msg.type_id == "LTE_PHY_PUCCH_Tx_Report":
            self.callback_pucch(msg)
        elif msg.type_id == "LTE_PHY_PUSCH_Tx_Report":
            self.callback_pusch_tx(msg)

    def callback_pdsch(self, msg):
        log_item = msg.data.decode()
        if 'Records' in log_item:
            for record in log_item['Records']:
                if 'DL transport block' in record:
                    tb = record['DL transport block']
                    modulation = tb.get('modulation', '')
                    if modulation in self.modulation_counts:
                        self.modulation_counts[modulation] += 1
                        self.broadcast_info(f"PDSCH Modulation: {modulation}, Count: {self.modulation_counts[modulation]}")

    def callback_pusch(self, msg):
        log_item = msg.data.decode()
        if 'Records' in log_item:
            for record in log_item['Records']:
                if 'CQI CW0' in record:
                    cqi = record['CQI CW0']
                    self.cqi_values.append(cqi)
                    self.broadcast_info(f"PUSCH CQI: {cqi}")

    def callback_pusch_grant(self, msg):
        log_item = msg.data.decode()
        uplink_bandwidth = 0
        grant_utilization = 0
        if 'UL transport block' in log_item:
            tb = log_item['UL transport block']
            uplink_bandwidth = tb.get('size', 0)
            grant_utilization = tb.get('grant', 0)
            self.broadcast_info(f"UL Bandwidth: {uplink_bandwidth}, Grant Utilization: {grant_utilization}")

    def callback_pucch(self, msg):
        log_item = msg.data.decode()
        if 'Records' in log_item:
            for record in log_item['Records']:
                if 'SR' in record:
                    self.broadcast_info(f"PUCCH SR Event: {record['SR']}")

    def callback_pusch_tx(self, msg):
        log_item = msg.data.decode()
        if 'Records' in log_item:
            for record in log_item['Records']:
                if 'Tx power' in record:
                    self.broadcast_info(f"PUSCH Tx Power: {record['Tx power']}")

    def predict_bw_modified(self):
        if not self.cqi_values:
            return
        cqi_to_bw_map = {0: 1.4, 1: 1.4, 2: 2.8, 3: 5, 4: 10, 5: 20}  # Example mapping
        avg_cqi = sum(self.cqi_values) / len(self.cqi_values)
        predicted_bw = cqi_to_bw_map.get(int(avg_cqi), 1.4)
        self.broadcast_info(f"Predicted DL Bandwidth: {predicted_bw} MHz")
