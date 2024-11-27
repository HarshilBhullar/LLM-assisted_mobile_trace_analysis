
#!/usr/bin/python
# Filename: mm_analysis_script.py

import os
import sys

"""
Offline analysis by replaying logs with a custom MmAnalyzer
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, MmAnalyzer

def calculate_total_span(service_log):
    total_duration = 0
    for span in service_log:
        if span.start and span.end:
            total_duration += (span.end - span.start).total_seconds()
    return total_duration

if __name__ == "__main__":

    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")

    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./decoded_messages.xml")
    logger.set_source(src)

    # Initialize the custom analyzer
    mm_analyzer = MmAnalyzer()
    mm_analyzer.set_source(src)

    # Start the monitoring
    src.run()

    # Calculate and print service durations
    lte_service_duration = calculate_total_span(mm_analyzer.get_lte_normal_service_log())
    umts_service_duration = calculate_total_span(mm_analyzer.get_umts_normal_service_log())

    print(f"Total LTE normal service duration: {lte_service_duration} seconds")
    print(f"Total UMTS normal service duration: {umts_service_duration} seconds")
