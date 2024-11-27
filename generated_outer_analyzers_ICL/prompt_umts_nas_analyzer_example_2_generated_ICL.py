
#!/usr/bin/python
# Filename: umts_nas_analysis.py

import os
import sys
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger
from umts_nas_analyzer import UmtsNasAnalyzer

def calculate_average_time_difference(log_timestamps):
    if len(log_timestamps) < 2:
        return None
    time_diffs = [t2 - t1 for t1, t2 in zip(log_timestamps[:-1], log_timestamps[1:])]
    avg_time_diff = sum(time_diffs, timedelta()) / len(time_diffs)
    return avg_time_diff.total_seconds()

if __name__ == "__main__":
    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")
    
    # Enable specific logs
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    # Set up a logger
    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./modified_test.txt")
    logger.set_source(src)

    # Setup the UMTS NAS Analyzer
    umts_nas_analyzer = UmtsNasAnalyzer()
    umts_nas_analyzer.set_source(src)

    # Run the offline replay analysis
    print("Starting UMTS NAS analysis...")
    src.run()
    print("UMTS NAS analysis completed.")

    # Calculate average time difference between messages
    log_timestamps = logger.get_logged_timestamps()
    avg_time_diff = calculate_average_time_difference(log_timestamps)

    if avg_time_diff is not None:
        print(f"Average time difference between messages: {avg_time_diff:.2f} seconds")
    else:
        print("Not enough messages to calculate an average time difference.")
