
#!/usr/bin/python
# Filename: offline-analysis-example-modified.py
import os
import sys

"""
Offline analysis by replaying logs with modified calculations
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, LtePhyAnalyzer

if __name__ == "__main__":

    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")
    # src.enable_log_all()

    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./test_modified.txt")
    logger.set_source(src)

    lte_phy_analyzer = LtePhyAnalyzer()
    lte_phy_analyzer.set_source(src)

    # Start the monitoring
    src.run()

    # Additional analysis or logging
    # For instance, calculate and log the average downlink bandwidth over the entire run
    total_dl_bw = lte_phy_analyzer.lte_dl_bw
    total_time = (lte_phy_analyzer.prev_timestamp_dl - lte_phy_analyzer.init_timestamp).total_seconds() if lte_phy_analyzer.init_timestamp else 1
    avg_dl_bw_mbps = (total_dl_bw / total_time) / 1000000.0

    print(f"Average Downlink Bandwidth: {avg_dl_bw_mbps:.2f} Mbps")
