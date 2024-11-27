
#!/usr/bin/python
# Filename: track-cell-info-outer-analyzer.py
import os
import sys

"""
Offline analysis by replaying LTE RRC logs and tracking cell information
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, TrackCellInfoAnalyzer

if __name__ == "__main__":

    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")
    # src.enable_log_all()

    src.enable_log("LTE_RRC_Serv_Cell_Info")
    src.enable_log("LTE_RRC_MIB_Packet")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./cell_info_log.txt")
    logger.set_source(src)

    track_cell_info_analyzer = TrackCellInfoAnalyzer()
    track_cell_info_analyzer.set_source(src)

    # Custom logic to calculate total bandwidth
    def calculate_total_bandwidth():
        dl_bandwidth = track_cell_info_analyzer.get_cur_downlink_bandwidth()
        ul_bandwidth = track_cell_info_analyzer.get_cur_uplink_bandwidth()
        if dl_bandwidth and ul_bandwidth:
            total_bandwidth = dl_bandwidth + ul_bandwidth
            print(f"Total Bandwidth: {total_bandwidth} MHz")
        else:
            print("Bandwidth information is incomplete.")

    # Start the monitoring
    src.run()

    # Perform custom bandwidth calculation after the run
    calculate_total_bandwidth()
