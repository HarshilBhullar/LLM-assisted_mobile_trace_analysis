
#!/usr/bin/python
# Filename: lte_phy_analyzer_modified.py
"""
A modified LTE PHY analyzer for enhanced analysis and metrics adjustment.

Author: Assistant
"""

from .analyzer import *
import xml.etree.ElementTree as ET

__all__ = ["LtePhyAnalyzerModified"]

class LtePhyAnalyzerModified(Analyzer):

    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)

        # Initialize internal states
        self.modulation_count = {'QPSK': 0, '16QAM': 0, '64QAM': 0}
        self.cqi_values = []
        self.uplink_bandwidth = 0
        self.ul_grant_utilization = 0
        self.sr_events = 0
        self.pusch_tx_power = 0

    def set_source(self, source):
        """
        Set the trace source. Enable the LTE PHY logs.

        :param source: the trace source.
        :type source: trace collector
        """
        Analyzer.set_source(self, source)

        source.enable_log("LTE_PHY_PDSCH_Stat_Indication")
        source.enable_log("LTE_PHY_PUSCH_CSF")
        source.enable_log("LTE_PHY_UL_Tx_Statistics")
        source.enable_log("LTE_PHY_PUCCH_Tx_Report")
        source.enable_log("LTE_PHY_PUSCH_Tx_Report")

    def __msg_callback(self, msg):
        """
        Callback to process incoming messages and dispatch to appropriate handlers.

        :param msg: the event (message) from the trace collector.
        """
        if msg.type_id == "LTE_PHY_PDSCH_Stat_Indication":
            self.callback_pdsch(msg)
        elif msg.type_id == "LTE_PHY_PUSCH_CSF":
            self.callback_pusch(msg)
        elif msg.type_id == "LTE_PHY_UL_Tx_Statistics":
            self.callback_pusch_grant(msg)
        elif msg.type_id == "LTE_PHY_PUCCH_Tx_Report":
            self.callback_pucch(msg)
        elif msg.type_id == "LTE_PHY_PUSCH_Tx_Report":
            self.callback_pusch_tx(msg)

    def callback_pdsch(self, msg):
        """
        Process PDSCH packets to compute downlink bandwidth and modulation schemes.

        :param msg: the PDSCH message.
        """
        log_item = msg.data.decode()
        modulation = log_item['Modulation']
        if modulation in self.modulation_count:
            self.modulation_count[modulation] += 1
        self.broadcast_info("PDSCH_Modulation_Count", self.modulation_count)

    def callback_pusch(self, msg):
        """
        Handle PUSCH CSF packets to update CQI values.

        :param msg: the PUSCH CSF message.
        """
        log_item = msg.data.decode()
        cqi = log_item['Wideband CQI']
        self.cqi_values.append(cqi)
        self.broadcast_info("PUSCH_CQI", self.cqi_values)

    def callback_pusch_grant(self, msg):
        """
        Process UL Tx Statistics to calculate uplink bandwidth and grant utilization.

        :param msg: the UL Tx Statistics message.
        """
        log_item = msg.data.decode()
        self.uplink_bandwidth = log_item['UL Bandwidth']
        self.ul_grant_utilization = log_item['Grant Utilization']
        self.broadcast_info("UL_Tx_Statistics", {
            'Uplink Bandwidth': self.uplink_bandwidth,
            'Grant Utilization': self.ul_grant_utilization
        })

    def callback_pucch(self, msg):
        """
        Capture and log PUCCH scheduling requests.

        :param msg: the PUCCH Tx Report message.
        """
        log_item = msg.data.decode()
        self.sr_events += log_item['SR Count']
        self.broadcast_info("PUCCH_SR_Events", self.sr_events)

    def callback_pusch_tx(self, msg):
        """
        Extract and log PUSCH transmission power details.

        :param msg: the PUSCH Tx Report message.
        """
        log_item = msg.data.decode()
        self.pusch_tx_power = log_item['Tx Power']
        self.broadcast_info("PUSCH_Tx_Power", self.pusch_tx_power)

    def predict_bw_modified(self):
        """
        Predict downlink bandwidth based on current CQI values with a modified mapping table.
        """
        if not self.cqi_values:
            predicted_bw = 0
        else:
            avg_cqi = sum(self.cqi_values) / len(self.cqi_values)
            predicted_bw = avg_cqi * 10  # Example mapping: CQI * 10
        self.broadcast_info("Predicted_Downlink_Bandwidth", predicted_bw)
