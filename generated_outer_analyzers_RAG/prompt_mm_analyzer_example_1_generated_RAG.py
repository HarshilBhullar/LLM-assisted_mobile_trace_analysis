
#!/usr/bin/python
# Filename: modified-mm-analysis-example.py

import os
import sys

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger
from mobile_insight.analyzer.mm_analyzer import MmAnalyzer

def print_additional_metrics(mm_analyzer):
    # Calculate the total duration of UMTS normal service spans
    umts_normal_service_log = mm_analyzer.get_umts_normal_service_log()
    umts_total_duration = sum((span.end - span.start).total_seconds() for span in umts_normal_service_log if span.end)

    # Calculate the total duration of LTE normal service spans
    lte_normal_service_log = mm_analyzer.get_lte_normal_service_log()
    lte_total_duration = sum((span.end - span.start).total_seconds() for span in lte_normal_service_log if span.end)

    print(f"Total UMTS normal service duration: {umts_total_duration} seconds")
    print(f"Total LTE normal service duration: {lte_total_duration} seconds")

if __name__ == "__main__":
    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")
    
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("5G_NR_RRC_OTA_Packet")

    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./modified_test.txt")
    logger.set_source(src)
    
    mm_analyzer = MmAnalyzer()
    mm_analyzer.set_source(src)  # bind with the monitor

    # Start the monitoring
    src.run()

    # Output the additional metrics
    print_additional_metrics(mm_analyzer)
