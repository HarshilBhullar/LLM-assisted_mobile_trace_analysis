
#!/usr/bin/python
# Filename: lte_rlc_offline_analysis.py

"""
Offline LTE RLC analyzer script using MobileInsight

Author: Haotian Deng
"""

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger
from lte_rlc_analyzer import LteRlcAnalyzer
import os

def main():
    try:
        # Initialize OfflineReplayer
        src = OfflineReplayer()
        log_directory = "/path/to/your/log/files"  # Change to your log directory
        src.set_input_path(log_directory)

        # Enable required LTE and 5G NR logs
        src.enable_log("LTE_PHY_Serv_Cell_Measurement")
        src.enable_log("5G_NR_RRC_OTA_Packet")
        src.enable_log("LTE_RRC_OTA_Packet")
        src.enable_log("LTE_MAC_Rach_Trigger")

        # Setup MsgLogger to decode and store logs
        msg_logger = MsgLogger()
        msg_logger.set_decode_format(MsgLogger.XML)
        msg_logger.save_decoded_msg_as("test_modified.txt")
        msg_logger.set_source(src)

        # Initialize and set up LteRlcAnalyzer
        rlc_analyzer = LteRlcAnalyzer()
        rlc_analyzer.set_source(src)

        # Start the offline analysis
        src.run()
        
    except Exception as e:
        print(f"An error occurred during execution: {e}")

if __name__ == "__main__":
    main()
