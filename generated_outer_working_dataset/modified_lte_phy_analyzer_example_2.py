
#!/usr/bin/python
# Filename: modified-offline-analysis-example.py
import os
import sys

"""
Modified offline analysis by replaying logs with additional metrics
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
    logger.save_decoded_msg_as("./modified_test.txt")
    logger.set_source(src)

    lte_phy_analyzer = LtePhyAnalyzer()
    lte_phy_analyzer.set_source(src)

    # Add additional log for monitoring
    def additional_logging_callback(msg):
        if msg.type_id == "LTE_PHY_PUCCH_Tx_Report":
            log_item = msg.data.decode()
            timestamp = str(log_item['timestamp'])
            pucch_tx_power = log_item['Records'][0]['PUCCH Tx Power (dBm)']
            logger.log_info(f"Additional Log - Timestamp: {timestamp}, PUCCH Tx Power: {pucch_tx_power}")

    lte_phy_analyzer.add_callback("LTE_PHY_PUCCH_Tx_Report", additional_logging_callback)

    # Start the monitoring
    src.run()
