
#!/usr/bin/python
# Filename: modified_offline_analysis.py

import os
import sys

"""
Modified offline analysis of cellular data logs
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, LteRlcAnalyzer

def main():
    # Initialize the data source
    src = OfflineReplayer()
    src.set_input_path("./logs/")
    
    # Selectively enable logs for analysis
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    # Configure the logger
    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./modified_test.txt")
    logger.set_source(src)

    # Integrate the LteRlcAnalyzer
    lte_rlc_analyzer = LteRlcAnalyzer()
    lte_rlc_analyzer.set_source(src)

    # Print starting point for modified analysis
    print("Starting modified offline analysis...")

    # Execute the analysis
    src.run()

if __name__ == "__main__":
    main()
