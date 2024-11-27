
#!/usr/bin/python
# Filename: umts-nas-analysis.py

import os
import sys

"""
UMTS NAS analysis by replaying logs with additional metric evaluation
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import UmtsNasAnalyzer, MsgLogger

def calculate_average_delay_class(analyzer):
    delay_classes = []

    def capture_delay_class(msg):
        if msg.type_id == "UMTS_NAS_MM_State":
            log_item = msg.data.decode()
            log_item_dict = dict(log_item)
            if 'Delay Class' in log_item_dict:
                delay_classes.append(int(log_item_dict['Delay Class']))

    analyzer.add_source_callback(capture_delay_class)

    def compute_average():
        if delay_classes:
            average_delay_class = sum(delay_classes) / len(delay_classes)
            print(f"Calculated Average Delay Class: {average_delay_class}")
        else:
            print("No delay class data available to calculate average.")

    return compute_average

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
    logger.save_decoded_msg_as("./umts_nas_decoded.txt")
    logger.set_source(src)

    umts_nas_analyzer = UmtsNasAnalyzer()
    umts_nas_analyzer.set_source(src)

    # Setup additional metric calculation
    compute_average = calculate_average_delay_class(umts_nas_analyzer)

    # Start the monitoring
    try:
        src.run()

        # Perform the additional metric calculation
        compute_average()

    except Exception as e:
        print(f"An error occurred during execution: {e}")
