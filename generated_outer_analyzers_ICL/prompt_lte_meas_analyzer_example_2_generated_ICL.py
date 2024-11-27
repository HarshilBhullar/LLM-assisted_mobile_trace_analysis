
#!/usr/bin/python
# Filename: lte_measurement_analysis.py

import os
import sys

"""
LTE radio measurement analysis using custom analyzer.
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, LteMeasurementAnalyzer

def log_additional_metrics(analyzer):
    """
    Function to compute and log additional metrics from LteMeasurementAnalyzer.
    """
    print("Fetching additional metrics...")

    rsrp_list = analyzer.get_rsrp_list()
    rsrq_list = analyzer.get_rsrq_list()

    if rsrp_list:
        avg_rsrp = sum(rsrp_list) / len(rsrp_list)
        print(f"Average RSRP: {avg_rsrp:.2f} dBm")

    if rsrq_list:
        avg_rsrq = sum(rsrq_list) / len(rsrq_list)
        print(f"Average RSRQ: {avg_rsrq:.2f} dB")


if __name__ == "__main__":

    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")

    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./modified_test.txt")
    logger.set_source(src)

    # Analyzer
    lte_measurement_analyzer = LteMeasurementAnalyzer()
    lte_measurement_analyzer.set_source(src)

    # Run the monitoring
    src.run()

    # Log additional metrics
    log_additional_metrics(lte_measurement_analyzer)
