
#!/usr/bin/python
# Filename: modified-offline-analysis-example.py
import os
import sys

"""
Offline analysis with LtePhyAnalyzer
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger
from lte_phy_analyzer import LtePhyAnalyzer

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

    lte_phy_analyzer = LtePhyAnalyzer()
    lte_phy_analyzer.set_source(src)

    def additional_logging_callback(event):
        log_item = event.data.decode()
        if "PUCCH Tx Power (dBm)" in log_item:
            timestamp = log_item['timestamp']
            pucch_tx_power = log_item['PUCCH Tx Power (dBm)']
            print(f"PUCCH Tx Power at {timestamp}: {pucch_tx_power} dBm")

    src.add_callback("LTE_PHY_PUCCH_Tx_Report", additional_logging_callback)

    # Start the monitoring
    src.run()
