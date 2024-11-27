
#!/usr/bin/python
# Filename: modified-offline-analysis-example.py

"""
Offline analysis by replaying logs with detailed LTE RRC cell information
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, TrackCellInfoAnalyzer

import os
import sys
import traceback

def modified_offline_analysis(input_path="./logs/"):
    
    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path(input_path)

    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./decoded_messages.txt")
    logger.set_source(src)

    # Initialize the TrackCellInfoAnalyzer
    track_cell_info_analyzer = TrackCellInfoAnalyzer()
    track_cell_info_analyzer.set_source(src)

    # Function to calculate the average downlink frequency
    def calculate_average_dl_frequency(analyzer):
        all_dl_frequencies = []
        
        def callback(msg):
            if msg.type_id == "LTE_RRC_Serv_Cell_Info":
                dl_freq = msg.data.decode().get('Downlink frequency', None)
                if dl_freq is not None:
                    all_dl_frequencies.append(dl_freq)
        
        analyzer.add_source_callback(callback)

        # Run the source to collect data
        src.run()

        if all_dl_frequencies:
            average_dl_freq = sum(all_dl_frequencies) / len(all_dl_frequencies)
            print(f"Average Downlink Frequency: {average_dl_freq} MHz")
        else:
            print("No downlink frequency data available.")

    try:
        # Perform the analysis
        calculate_average_dl_frequency(track_cell_info_analyzer)
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
    else:
        input_path = "./logs/"
    modified_offline_analysis(input_path)
