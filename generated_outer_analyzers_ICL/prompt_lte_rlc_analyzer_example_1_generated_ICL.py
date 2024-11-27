
#!/usr/bin/python
# Filename: modified_offline_analysis.py

import os
import sys

"""
Modified Offline analysis using LteRlcAnalyzer
"""

# Import MobileInsight modules
from mobileinsight.monitor import OfflineReplayer
from mobileinsight.analyzer import MsgLogger, LteRlcAnalyzer

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

    lte_rlc_analyzer = LteRlcAnalyzer()
    lte_rlc_analyzer.set_source(src)  # bind with the monitor

    # Print a statement to indicate the start of the analysis
    print("Starting modified offline analysis...")

    # Start the monitoring
    src.run()
