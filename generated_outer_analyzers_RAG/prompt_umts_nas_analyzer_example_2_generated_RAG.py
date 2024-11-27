
#!/usr/bin/python
# Filename: umts-nas-offline-analysis.py

import os
import sys

"""
Offline analysis for UMTS NAS layer logs
"""

# Import necessary modules from MobileInsight
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger
from umts_nas_analyzer import UmtsNasAnalyzer

if __name__ == "__main__":

    # Initialize the offline replayer
    src = OfflineReplayer()
    src.set_input_path("./logs/")

    # Enable specific logs for analysis
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    # Set up the message logger
    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./modified_test.txt")
    logger.set_source(src)

    # Set up the UMTS NAS analyzer
    umts_nas_analyzer = UmtsNasAnalyzer()
    umts_nas_analyzer.set_source(src)

    # Run the analysis
    src.run()

    # Additional Processing: Calculate average time difference between consecutive messages
    log_file_path = "./modified_test.txt"
    try:
        with open(log_file_path, "r") as log_file:
            timestamps = []
            for line in log_file:
                if "timestamp" in line:
                    timestamp_str = line.split("timestamp=")[-1].strip().strip('"')
                    timestamps.append(timestamp_str)

            if len(timestamps) > 1:
                time_diffs = []
                for i in range(1, len(timestamps)):
                    time1 = datetime.datetime.strptime(timestamps[i-1], "%Y-%m-%d %H:%M:%S.%f")
                    time2 = datetime.datetime.strptime(timestamps[i], "%Y-%m-%d %H:%M:%S.%f")
                    time_diff = (time2 - time1).total_seconds()
                    time_diffs.append(time_diff)

                avg_time_diff = sum(time_diffs) / len(time_diffs)
                print(f"Average time difference between consecutive messages: {avg_time_diff:.6f} seconds")
            else:
                print("Not enough messages to calculate average time difference.")

    except Exception as e:
        print(f"Error processing log file: {e}")
