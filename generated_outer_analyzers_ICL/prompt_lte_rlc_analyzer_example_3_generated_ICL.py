
#!/usr/bin/python
# Filename: offline-analysis-lte-rlc.py

import os
import sys

"""
Offline analysis by replaying LTE RLC logs
"""

# Import MobileInsight modules
from mobileinsight.monitor import OfflineReplayer
from mobileinsight.analyzer import MsgLogger, LteRlcAnalyzer

if __name__ == "__main__":

    try:
        # Initialize a monitor
        src = OfflineReplayer()
        src.set_input_path("./logs/")

        # Enable specific logs
        src.enable_log("LTE_PHY_Serv_Cell_Measurement")
        src.enable_log("5G_NR_RRC_OTA_Packet")
        src.enable_log("LTE_RRC_OTA_Packet")
        src.enable_log("LTE_MAC_Rach_Trigger")

        # Set up the logger
        logger = MsgLogger()
        logger.set_decode_format(MsgLogger.XML)
        logger.set_dump_type(MsgLogger.FILE_ONLY)
        logger.save_decoded_msg_as("./test_modified.txt")
        logger.set_source(src)

        # Set up the analyzer
        lte_rlc_analyzer = LteRlcAnalyzer()
        lte_rlc_analyzer.set_source(src)

        # Start the monitoring
        src.run()

    except Exception as e:
        print(f"An error occurred: {e}")
