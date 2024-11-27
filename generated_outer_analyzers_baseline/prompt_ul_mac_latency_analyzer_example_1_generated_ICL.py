
#!/usr/bin/python
# Filename: run_ul_mac_latency_analysis.py

import os
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger
from ul_mac_latency_analyzer import UlMacLatencyAnalyzer

def main(log_dir):
    # Initialize the Offline Replayer
    src = OfflineReplayer()
    src.set_input_path(log_dir)

    # Enable specific logs
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    # Initialize MsgLogger
    logger = MsgLogger()
    logger.set_source(src)
    logger.set_decoding(MsgLogger.XML)
    logger.save_decoded_logs("modified_test.txt")

    # Initialize UlMacLatencyAnalyzer
    ul_mac_latency_analyzer = UlMacLatencyAnalyzer()
    ul_mac_latency_analyzer.set_source(src)

    # Callback function to log MAC UL buffer queue length
    def log_queue_length():
        print(f"Current MAC UL buffer queue length: {ul_mac_latency_analyzer.queue_length}")

    src.set_end_callback(log_queue_length)

    # Run the analysis
    src.run()

if __name__ == "__main__":
    log_directory = "/path/to/your/log/files"  # Update this path to your log files directory
    main(log_directory)
