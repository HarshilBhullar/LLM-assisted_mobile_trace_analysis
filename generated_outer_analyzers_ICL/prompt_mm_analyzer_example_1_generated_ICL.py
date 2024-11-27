
#!/usr/bin/python
# Filename: mm_analyzer_outer.py
import os
import sys

"""
Offline analysis by replaying logs using MmAnalyzer
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, MmAnalyzer

def print_additional_metrics(mm_analyzer):
    # Calculate and print total UMTS and LTE normal service durations
    umts_duration = sum((span.end - span.start).total_seconds() for span in mm_analyzer.get_umts_normal_service_log() if span.end)
    lte_duration = sum((span.end - span.start).total_seconds() for span in mm_analyzer.get_lte_normal_service_log() if span.end)
    
    print("Total UMTS normal service duration: ", umts_duration, " seconds")
    print("Total LTE normal service duration: ", lte_duration, " seconds")

if __name__ == "__main__":

    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")
    src.enable_log_all()

    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./modified_test.txt")
    logger.set_source(src)

    mm_analyzer = MmAnalyzer()
    mm_analyzer.set_source(src)

    # Start the monitoring
    src.run()

    # Print additional metrics
    print_additional_metrics(mm_analyzer)
