
#!/usr/bin/python
# Filename: lte_phy_analyzer_modified.py
"""
Enhanced LTE PHY Analyzer with bandwidth prediction and modulation statistics

Author: Yuanjie Li (Modified)
"""

from mobile_insight.analyzer.analyzer import *

__all__ = ["LtePhyAnalyzerModified"]

class LtePhyAnalyzerModified(Analyzer):

    def __init__(self):
        Analyzer.__init__(self)

        self.add_source_callback(self.__msg_callback)

        # Initialize variables and counters
        self.dl_bandwidth = 0
        self.ul_bandwidth = 0
        self.cqi_values = []

    def set_source(self, source):
        """
        Set the trace source. Enable the LTE PHY layer logs.

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)

        # Enable specific LTE PHY layer logs
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

        # Log the original message
        self.log_info("PDSCH Packet: " + str(log_item))

        # Process downlink bandwidth and modulation statistics
        # Example: Calculate bandwidth based on some fields in log_item
        # self.dl_bandwidth = ...
        # Example: Extract and log modulation info
        # modulation = log_item.get("Modulation")
        # self.log_info(f"Modulation: {modulation}")

        # Predict bandwidth using current CQI values
        self.predict_bw()

    def __process_pusch_csf(self, msg):
        log_item = msg.data.decode()

        # Log the original message
        self.log_info("PUSCH CSF: " + str(log_item))

        # Capture and log CQI values
        # cqi = log_item.get("CQI")
        # self.cqi_values.append(cqi)
        # self.log_info(f"CQI: {cqi}")

    def __process_ul_tx_statistics(self, msg):
        log_item = msg.data.decode()

        # Log the original message
        self.log_info("UL Tx Statistics: " + str(log_item))

        # Determine uplink bandwidth utilization
        # self.ul_bandwidth = ...

    def __process_pucch_tx_report(self, msg):
        log_item = msg.data.decode()

        # Log the original message
        self.log_info("PUCCH Tx Report: " + str(log_item))

        # Analyze PUCCH scheduling requests and related SR events

    def __process_pusch_tx_report(self, msg):
        log_item = msg.data.decode()

        # Log the original message
        self.log_info("PUSCH Tx Report: " + str(log_item))

        # Log power measurements related to PUSCH transmissions

    def predict_bw(self):
        # Example CQI to bandwidth mapping
        cqi_to_bw = {
            1: 1.4,
            2: 3,
            3: 5,
            # ...
            15: 20
        }

        # Calculate predicted bandwidth based on average CQI
        if self.cqi_values:
            avg_cqi = sum(self.cqi_values) / len(self.cqi_values)
            predicted_bw = cqi_to_bw.get(int(avg_cqi), 0)
            self.log_info(f"Predicted Downlink Bandwidth: {predicted_bw} MHz")
            self.broadcast_info("PREDICTED_DL_BW", {"bandwidth": predicted_bw})
