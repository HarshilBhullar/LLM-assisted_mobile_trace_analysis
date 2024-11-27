
#!/usr/bin/python
# Filename: outer_mm_analyzer.py

import os
import datetime
from mobile_insight.analyzer import OfflineReplayer
from mobile_insight.analyzer import MsgLogger
from mm_analyzer import MmAnalyzer

def calculate_total_span(spans):
    total_duration = datetime.timedelta()
    for span in spans:
        if span.start and span.end:
            total_duration += (span.end - span.start)
    return total_duration.total_seconds()

def main():
    # Initialize the OfflineReplayer
    log_directory = "/path/to/log/directory"  # Specify the directory containing logs
    offline_replayer = OfflineReplayer()
    offline_replayer.set_input_path(log_directory)

    # Enable necessary logs for analysis
    offline_replayer.enable_log("LTE_NAS_EMM_State")
    offline_replayer.enable_log("LTE_RRC_OTA_Packet")
    offline_replayer.enable_log("UMTS_NAS_GMM_State")
    offline_replayer.enable_log("UMTS_NAS_OTA_Packet")

    # Initialize MsgLogger for logging decoded messages
    msg_logger = MsgLogger()
    msg_logger.set_source(offline_replayer)
    msg_logger.set_decoding_format("xml")
    msg_logger.save_decoded_msg_as("output_file.xml")  # Specify the output file for decoded messages

    # Instantiate the custom MmAnalyzer
    mm_analyzer = MmAnalyzer()
    mm_analyzer.set_source(offline_replayer)

    # Run the OfflineReplayer
    offline_replayer.run()

    # Calculate total durations for LTE and UMTS normal service spans
    lte_normal_service_spans = mm_analyzer.get_lte_normal_service_log()
    umts_normal_service_spans = mm_analyzer.get_umts_normal_service_log()

    total_lte_duration = calculate_total_span(lte_normal_service_spans)
    total_umts_duration = calculate_total_span(umts_normal_service_spans)

    # Output the calculated durations
    print(f"Total LTE normal service duration: {total_lte_duration} seconds")
    print(f"Total UMTS normal service duration: {total_umts_duration} seconds")

if __name__ == "__main__":
    main()
