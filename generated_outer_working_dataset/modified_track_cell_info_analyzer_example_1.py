
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
    logger.save_decoded_msg_as("./modified_test.txt")
    logger.set_source(src)

    track_cell_info_analyzer = TrackCellInfoAnalyzer()
    track_cell_info_analyzer.set_source(src)

    # Additional analysis: Calculate and print average downlink frequency
    def calculate_average_dl_frequency():
        total_dl_freq = 0
        count = 0
        for log_item in src.get_decoded_messages():
            if log_item.type_id == "LTE_RRC_Serv_Cell_Info":
                total_dl_freq += log_item.data['Downlink frequency']
                count += 1
        return total_dl_freq / count if count > 0 else 0

    avg_dl_frequency = calculate_average_dl_frequency()
    print(f"Average Downlink Frequency: {avg_dl_frequency} MHz")

    # Start the monitoring
    src.run()
