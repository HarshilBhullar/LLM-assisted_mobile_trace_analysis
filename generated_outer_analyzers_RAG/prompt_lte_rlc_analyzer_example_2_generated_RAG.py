
#!/usr/bin/python
# Filename: outer_analyzer.py

import os
import sys

"""
Outer analyzer script utilizing LteRlcAnalyzer
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, LteRlcAnalyzer

if __name__ == "__main__":

    try:
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
        logger.save_decoded_msg_as("./modified_test.txt")
        logger.set_source(src)

        lte_rlc_analyzer = LteRlcAnalyzer()
        lte_rlc_analyzer.set_source(src)

        # Indicate start of the analysis
        print("Starting analysis...")

        # Start the monitoring
        src.run()

        # Indicate completion of the analysis
        print("Analysis completed successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")
