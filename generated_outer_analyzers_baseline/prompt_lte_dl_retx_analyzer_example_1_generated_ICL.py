
#!/usr/bin/python
# Filename: custom_offline_analyzer.py

"""
Script to perform offline analysis of mobile network logs using MobileInsight.
"""

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger
from lte_dl_retx_analyzer import LteDlRetxAnalyzer
import os
import sys

def calculate_average_rlc_retx_delay(analyzer):
    total_delay = 0
    total_count = 0

    for bearer in analyzer.bearer_entity.values():
        for retx in bearer.rlc_retx:
            total_delay += retx['rlc_retx']
            total_count += 1

    if total_count == 0:
        return 0  # Avoid division by zero

    return total_delay / total_count

def main():
    log_dir = "/path/to/log/directory"  # Set the correct path to your log directory

    # Initialize OfflineReplayer
    replayer = OfflineReplayer()
    replayer.set_input_path(log_dir)
    
    # Enable specific logs for analysis
    replayer.enable_log("LTE_PHY_Serv_Cell_Measurement")
    replayer.enable_log("5G_NR_RRC_OTA_Packet")
    replayer.enable_log("LTE_RRC_OTA_Packet")
    replayer.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    # Initialize custom analyzer
    lte_dl_retx_analyzer = LteDlRetxAnalyzer()
    lte_dl_retx_analyzer.set_source(replayer)

    # Setup message logger
    logger = MsgLogger()
    logger.set_source(replayer)
    logger.set_decoding(MsgLogger.XML)
    logger.save_decoded_msg_as("test.txt")

    try:
        # Run the replayer to process logs
        replayer.run()

        # Calculate and print the average RLC retransmission delay
        avg_rlc_retx_delay = calculate_average_rlc_retx_delay(lte_dl_retx_analyzer)
        print(f"Average RLC Retransmission Delay: {avg_rlc_retx_delay} ms")

    except Exception as e:
        print(f"Error during log processing: {e}")

if __name__ == "__main__":
    main()
