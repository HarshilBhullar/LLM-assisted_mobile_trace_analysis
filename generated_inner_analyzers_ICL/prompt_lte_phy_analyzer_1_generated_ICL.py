
#!/usr/bin/python
# Filename: lte_phy_analyzer_modified.py
"""
A modified LTE PHY analyzer for enhanced bandwidth prediction and modulation statistics.

Author: [Your Name]
"""

from .analyzer import *
import xml.etree.ElementTree as ET

__all__ = ["LtePhyAnalyzerModified"]

class LtePhyAnalyzerModified(Analyzer):

    """
    A protocol analyzer for LTE PHY layer with enhanced metrics.
    """
    def __init__(self):

        Analyzer.__init__(self)

        # Initialize internal states
        self.dl_bandwidth = 0
        self.ul_bandwidth = 0
        self.cqi_values = []
        self.modulation_stats = {"QPSK": 0, "16QAM": 0, "64QAM": 0}
        self.add_source_callback(self.__msg_callback)

    def __msg_callback(self, msg):
        """
        Callback to process LTE PHY messages.

        :param msg: the event (message) from the trace collector.
        """
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
        log_item_dict = dict(log_item)
        # Example processing: Extracting modulation type and CQI
        modulation = log_item_dict.get('Modulation')
        cqi = log_item_dict.get('CQI', None)
        if modulation:
            self.modulation_stats[modulation] += 1
        if cqi:
            self.cqi_values.append(int(cqi))
        self.dl_bandwidth = self.predict_bw(self.cqi_values)
        self.log_info(f"DL Bandwidth: {self.dl_bandwidth}")
        self.broadcast_info("DL_BANDWIDTH", self.dl_bandwidth)

    def __process_pusch_csf(self, msg):
        log_item = msg.data.decode()
        log_item_dict = dict(log_item)
        cqi = log_item_dict.get('CQI', None)
        if cqi:
            self.cqi_values.append(int(cqi))

    def __process_ul_tx_statistics(self, msg):
        log_item = msg.data.decode()
        log_item_dict = dict(log_item)
        # Example processing: Extracting UL bandwidth information
        self.ul_bandwidth = log_item_dict.get('UL Bandwidth', 0)
        self.log_info(f"UL Bandwidth: {self.ul_bandwidth}")
        self.broadcast_info("UL_BANDWIDTH", self.ul_bandwidth)

    def __process_pucch_tx_report(self, msg):
        log_item = msg.data.decode()
        log_item_dict = dict(log_item)
        # Process PUCCH related information

    def __process_pusch_tx_report(self, msg):
        log_item = msg.data.decode()
        log_item_dict = dict(log_item)
        # Process PUSCH power measurements

    def predict_bw(self, cqi_values):
        """
        Predicts downlink bandwidth based on current CQI values.

        :param cqi_values: a list of CQI values
        :return: predicted bandwidth
        """
        cqi_to_bw_mapping = {0: 1.4, 1: 2.8, 2: 5.6, 3: 11.2, 4: 22.4, 5: 28.0, 6: 33.6, 7: 50.4, 8: 56.0, 9: 67.2, 10: 78.4, 11: 84.0, 12: 100.8, 13: 112.0, 14: 123.2, 15: 140.8}
        avg_cqi = sum(cqi_values) / len(cqi_values) if cqi_values else 0
        predicted_bw = cqi_to_bw_mapping.get(int(avg_cqi), 0)
        self.log_info(f"Predicted DL Bandwidth: {predicted_bw}")
        return predicted_bw

    def set_source(self, source):
        """
        Set the trace source. Enable the LTE PHY messages.

        :param source: the trace source.
        """
        Analyzer.set_source(self, source)
        source.enable_log("LTE_PHY_PDSCH_Packet")
        source.enable_log("LTE_PHY_PUSCH_CSF")
        source.enable_log("LTE_MAC_UL_Tx_Statistics")
        source.enable_log("LTE_PHY_PUCCH_Tx_Report")
        source.enable_log("LTE_PHY_PUSCH_Tx_Report")
