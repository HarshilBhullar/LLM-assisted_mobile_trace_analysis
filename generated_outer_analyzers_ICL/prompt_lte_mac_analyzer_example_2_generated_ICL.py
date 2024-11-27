
#!/usr/bin/python
# Filename: lte_mac_analysis.py

import os
import sys

"""
Offline analysis using LteMacAnalyzer with additional metrics
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger
from lte_mac_analyzer import LteMacAnalyzer

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
    logger.save_decoded_msg_as("./decoded_messages.xml")
    logger.set_source(src)

    lte_mac_analyzer = LteMacAnalyzer()
    lte_mac_analyzer.set_source(src)

    # Custom metric processing after log replay
    def custom_metric_processing():
        # Placeholder for custom metric calculations
        print("Custom metric processing completed.")

    # Start the monitoring
    src.run()

    # Execute custom metric processing
    custom_metric_processing()
