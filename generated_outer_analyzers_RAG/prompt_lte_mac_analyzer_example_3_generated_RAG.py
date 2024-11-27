
#!/usr/bin/python
# Filename: modified-lte-mac-analysis-example.py

import os
import sys

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, LteMacAnalyzer

"""
This script performs an offline analysis of LTE MAC layer logs
to evaluate UL grant utilization and buffering status.
"""

if __name__ == "__main__":

    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")

    # Enable necessary logs
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")
    src.enable_log("LTE_MAC_UL_Tx_Statistics")

    # Initialize and set the analyzer
    lte_mac_analyzer = LteMacAnalyzer()
    lte_mac_analyzer.set_source(src)

    # Optional: Setup message logger
    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./test_modified.txt")
    logger.set_source(src)

    # Start the monitoring
    src.run()

