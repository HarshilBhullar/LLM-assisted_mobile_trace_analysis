
#!/usr/bin/python
# Filename: offline-analysis-modified-example.py
import os
import sys

"""
Offline analysis by replaying logs with modified metrics
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

    # New processing step: Calculate enhanced metric
    def calculate_enhanced_metric():
        print("Calculating enhanced metrics...")
        # Example metric calculation (could be more complex in a real scenario)
        for bearer_id, bearer_entity in lte_dl_retx_analyzer.bearer_entity.items():
            total_mac_retx = sum([entry['mac_retx'] for entry in bearer_entity.mac_retx])
            total_rlc_retx = sum([entry['rlc_retx'] for entry in bearer_entity.rlc_retx])
            print(f"Bearer ID {bearer_id} - Total MAC Retx: {total_mac_retx}, Total RLC Retx: {total_rlc_retx}")

    # Start the monitoring
    src.run()

    # Perform the enhanced metric calculation after monitoring
    calculate_enhanced_metric()
