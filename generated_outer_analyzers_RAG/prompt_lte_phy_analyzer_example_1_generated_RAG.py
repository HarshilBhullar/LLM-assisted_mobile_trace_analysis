
#!/usr/bin/python
# Filename: modified-offline-analysis-example.py
import os
import sys

"""
Modified offline analysis by replaying logs
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, LtePhyAnalyzer

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

    lte_phy_analyzer = LtePhyAnalyzer()
    lte_phy_analyzer.set_source(src)

    # Start the monitoring
    src.run()

    # Calculate additional metrics
    def calculate_average_dl_bandwidth():
        total_dl_bandwidth = 0
        total_duration = 0
        def callback(event):
            nonlocal total_dl_bandwidth, total_duration
            if event.type_id == 'LTE_DL_BW':
                bandwidth = float(event.data['Bandwidth (Mbps)'])
                duration = lte_phy_analyzer.avg_window
                total_dl_bandwidth += bandwidth * duration
                total_duration += duration

        lte_phy_analyzer.add_callback(callback)
        average_dl_bandwidth = total_dl_bandwidth / total_duration if total_duration else 0
        print(f"Average Downlink Bandwidth: {average_dl_bandwidth:.2f} Mbps")

    calculate_average_dl_bandwidth()
