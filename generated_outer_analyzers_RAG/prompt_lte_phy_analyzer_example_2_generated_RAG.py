
#!/usr/bin/python
# Filename: lte_phy_analysis.py

import os
import sys

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger
from lte_phy_analyzer import LtePhyAnalyzer

def additional_logging_callback(event):
    if event.type_id == "LTE_PHY_PUCCH_Tx_Report":
        pucch_tx_power = event.data['PUCCH Tx Power (dBm)']
        print(f"PUCCH Tx Power: {pucch_tx_power} dBm")

if __name__ == "__main__":
    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")

    # Enable specific logs for LTE and 5G measurements
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    # Set up MsgLogger
    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./modified_test.txt")
    logger.set_source(src)

    # Instantiate LtePhyAnalyzer
    lte_phy_analyzer = LtePhyAnalyzer()
    lte_phy_analyzer.set_source(src)  # bind with the monitor

    # Register callback to log PUCCH Tx Power details
    lte_phy_analyzer.add_callback(additional_logging_callback)

    # Start the monitoring
    src.run()
