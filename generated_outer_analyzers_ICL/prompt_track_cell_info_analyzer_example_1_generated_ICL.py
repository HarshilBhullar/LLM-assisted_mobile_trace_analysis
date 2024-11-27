
#!/usr/bin/python
# Filename: modified-offline-analysis.py
import os
import sys

"""
Modified offline analysis by replaying logs
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, TrackCellInfoAnalyzer

def calculate_average_dl_frequency(decoded_msgs):
    total_dl_freq = 0
    count = 0
    for msg in decoded_msgs:
        if msg.type_id == "LTE_RRC_Serv_Cell_Info":
            total_dl_freq += msg.data['Downlink frequency']
            count += 1
    if count > 0:
        average_dl_freq = total_dl_freq / count
        print(f"Average Downlink Frequency: {average_dl_freq} MHz")
    else:
        print("No LTE_RRC_Serv_Cell_Info messages found for average calculation.")

if __name__ == "__main__":
    try:
        # Initialize a monitor
        src = OfflineReplayer()
        if len(sys.argv) > 1:
            src.set_input_path(sys.argv[1])
        else:
            src.set_input_path("./logs/")
        
        src.enable_log("LTE_PHY_Serv_Cell_Measurement")
        src.enable_log("5G_NR_RRC_OTA_Packet")
        src.enable_log("LTE_RRC_OTA_Packet")
        src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

        logger = MsgLogger()
        logger.set_decode_format(MsgLogger.XML)
        logger.set_dump_type(MsgLogger.FILE_ONLY)
        logger.save_decoded_msg_as("./output.txt")
        logger.set_source(src)

        track_cell_info_analyzer = TrackCellInfoAnalyzer()
        track_cell_info_analyzer.set_source(src)

        # Start the monitoring
        print("Starting the modified offline analysis...")
        src.run()
        print("Analysis completed.")

        # Perform additional analysis
        calculate_average_dl_frequency(logger.decoded_msgs)

    except Exception as e:
        print(f"An error occurred during analysis: {e}")
