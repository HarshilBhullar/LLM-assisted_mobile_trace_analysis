
#!/usr/bin/python
# Filename: modified-offline-analysis-example.py
import os
import sys

"""
Modified offline analysis by replaying logs with additional metrics
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, UmtsNasAnalyzer

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
    logger.save_decoded_msg_as("./modified_test.txt")  # Save to a different file
    logger.set_source(src)

    umts_nas_analyzer = UmtsNasAnalyzer()
    umts_nas_analyzer.set_source(src)

    # Start the monitoring
    src.run()

    # Additional processing: Calculate the average time between messages
    timestamps = []
    for msg in logger.get_decoded_messages():
        timestamps.append(msg.timestamp)

    if timestamps:
        time_diffs = [t - s for s, t in zip(timestamps, timestamps[1:])]
        avg_time_diff = sum(time_diffs, 0.0) / len(time_diffs)
        print(f"Average time between messages: {avg_time_diff} seconds")
    else:
        print("No messages found for average time calculation.")
