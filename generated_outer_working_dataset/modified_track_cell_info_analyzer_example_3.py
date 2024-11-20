
#!/usr/bin/python
# Filename: modified-offline-analysis-example.py
import os
import sys

"""
Modified offline analysis by replaying logs
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, TrackCellInfoAnalyzer

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
    logger.save_decoded_msg_as("./modified_test.txt")  # Changed output file name
    logger.set_source(src)

    track_cell_info_analyzer = TrackCellInfoAnalyzer()
    track_cell_info_analyzer.set_source(src)

    # Start the monitoring
    src.run()

    # Additional processing: retrieve and print current cell information
    print("Current Cell ID:", track_cell_info_analyzer.get_cur_cell_id())
    print("Current Downlink Frequency:", track_cell_info_analyzer.get_cur_downlink_frequency())
    print("Current Uplink Frequency:", track_cell_info_analyzer.get_cur_uplink_frequency())
    print("Current Operator:", track_cell_info_analyzer.get_cur_op())
    print("Current Band Indicator:", track_cell_info_analyzer.get_cur_band_indicator())
