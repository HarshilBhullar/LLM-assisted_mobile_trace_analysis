
#!/usr/bin/python
# Filename: mm_analysis.py
import os
import sys

"""
Offline analysis by replaying logs with MmAnalyzer
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, MmAnalyzer


def calculate_total_span(span_list):
    total_duration = 0
    for span in span_list:
        if span.start and span.end:
            total_duration += (span.end - span.start).total_seconds()
    return total_duration


if __name__ == "__main__":

    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")
    
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_NAS_EMM_State")
    src.enable_log("WCDMA_RRC_OTA_Packet")
    
    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./mm_analysis_output.txt")
    logger.set_source(src)

    mm_analyzer = MmAnalyzer()
    mm_analyzer.set_source(src)

    # Start the monitoring
    src.run()

    # Calculate and print total durations
    lte_service_spans = mm_analyzer.get_lte_normal_service_log()
    umts_service_spans = mm_analyzer.get_umts_normal_service_log()

    total_lte_duration = calculate_total_span(lte_service_spans)
    total_umts_duration = calculate_total_span(umts_service_spans)

    print(f"Total LTE Normal Service Duration: {total_lte_duration} seconds")
    print(f"Total UMTS Normal Service Duration: {total_umts_duration} seconds")
