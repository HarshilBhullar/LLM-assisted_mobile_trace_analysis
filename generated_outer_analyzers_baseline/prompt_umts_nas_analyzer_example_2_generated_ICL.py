
#!/usr/bin/python
# Filename: umts_nas_outer_analyzer.py

from mobile_insight.analyzer import MsgLogger
from mobile_insight.monitor import OfflineReplayer
from umts_nas_analyzer import UmtsNasAnalyzer
import os

def main():
    # Initialization
    replayer = OfflineReplayer()
    
    # Configuration
    replayer.set_input_path("./logs/")
    replayer.enable_log("LTE_PHY_Serv_Cell_Measurement")
    replayer.enable_log("5G_NR_RRC_OTA_Packet")
    replayer.enable_log("LTE_RRC_OTA_Packet")
    replayer.enable_log("LTE_NB1_ML1_GM_DCI_Info")
    
    # Logger Setup
    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.JSON)
    logger.save_decoded_msg_as("modified_test.txt")
    logger.set_source(replayer)
    
    # Analyzer Setup
    nas_analyzer = UmtsNasAnalyzer()
    nas_analyzer.set_source(replayer)
    
    # Execution
    replayer.run()

    # Additional Processing
    timestamps = logger.get_decoded_msg_timestamps()
    if len(timestamps) > 1:
        time_differences = [t2 - t1 for t1, t2 in zip(timestamps[:-1], timestamps[1:])]
        avg_time_diff = sum(time_differences) / len(time_differences)
        print("Average time difference between messages: {:.2f} seconds".format(avg_time_diff))
    else:
        print("No sufficient messages for calculating average time difference.")

if __name__ == "__main__":
    main()
