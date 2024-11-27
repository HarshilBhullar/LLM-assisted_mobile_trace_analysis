
#!/usr/bin/python
# Filename: umts_nas_outer_analyzer.py

import os
import sys
import traceback

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, UmtsNasAnalyzer

def umts_nas_analysis():
    # Initialize an OfflineReplayer
    src = OfflineReplayer()
    src.set_input_path("./logs/")

    # Enable additional LTE and 5G logs for comprehensive metrics
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    # Initialize the UmtsNasAnalyzer
    umts_nas_analyzer = UmtsNasAnalyzer()
    umts_nas_analyzer.set_source(src)  # Bind with the monitor

    # Save decoded messages to a specified file
    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./umts_nas_decoded.txt")
    logger.set_source(src)

    # Run the OfflineReplayer
    src.run()

    return umts_nas_analyzer

def calculate_average_delay_class(analyzer):
    delay_classes = []

    def callback(event):
        if event.type_id == "UMTS_NAS_MM_State":
            delay_classes.append(event.data["MM State"])

    analyzer.add_callback(callback)

    src.run()

    if delay_classes:
        average_delay_class = sum(delay_classes) / len(delay_classes)
        print(f"Average Delay Class: {average_delay_class}")
    else:
        print("No delay class data found.")

if __name__ == "__main__":
    try:
        analyzer = umts_nas_analysis()
        calculate_average_delay_class(analyzer)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        traceback.print_exc()
