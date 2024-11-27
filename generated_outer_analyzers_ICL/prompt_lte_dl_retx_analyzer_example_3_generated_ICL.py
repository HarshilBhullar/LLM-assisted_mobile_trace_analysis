
#!/usr/bin/python
# Filename: modified-offline-analysis-example.py
import os
import sys

"""
Offline analysis by replaying logs and evaluating retransmission metrics
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, LteDlRetxAnalyzer

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

    lte_dl_retx_analyzer = LteDlRetxAnalyzer()
    lte_dl_retx_analyzer.set_source(src)

    # New functionality: Calculate and log enhanced retransmission metrics
    def calculate_enhanced_metric():
        for cfg_idx, entity in lte_dl_retx_analyzer.bearer_entity.items():
            total_mac_retx = len(entity.mac_retx)
            total_rlc_retx = len(entity.rlc_retx)
            print(f"Radio Bearer {cfg_idx} - Total MAC Retransmissions: {total_mac_retx}, Total RLC Retransmissions: {total_rlc_retx}")

    # Start the monitoring
    src.run()

    # Calculate and print enhanced retransmission metrics after monitoring
    calculate_enhanced_metric()
