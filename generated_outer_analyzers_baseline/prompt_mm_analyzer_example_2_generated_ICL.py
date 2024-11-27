
#!/usr/bin/python
# Filename: outer_mm_analyzer.py

import sys
import os
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger
from custom_analyzer_module import MmAnalyzer

def main(log_directory):
    if not os.path.exists(log_directory):
        print(f"Error: Directory {log_directory} does not exist.")
        sys.exit(1)

    # Initialize OfflineReplayer
    src = OfflineReplayer()
    src.set_input_path(log_directory)

    # Enable specific log types
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    # Initialize and configure MsgLogger
    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_output_path("modified_test.txt")

    # Attach logger to OfflineReplayer
    src.add_trace_listener(logger)

    # Instantiate the MmAnalyzer and set its source to the OfflineReplayer
    analyzer = MmAnalyzer()
    analyzer.set_source(src)

    # Define a custom callback for counting LTE attach attempts
    attach_attempts = 0

    def custom_callback(event):
        nonlocal attach_attempts
        log_item = event.data.decode()
        if "Attach request" in log_item:
            attach_attempts += 1

    # Register the custom callback
    src.add_source_callback("LTE_NAS_EMM_Plain_OTA_Incoming_Packet", custom_callback)

    try:
        # Start the replay process
        src.run()
    except Exception as e:
        print(f"Error during analysis: {e}")
        sys.exit(1)

    # Output calculated metrics
    print(f"Number of LTE attach attempts: {attach_attempts}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python outer_mm_analyzer.py <log_directory>")
        sys.exit(1)

    log_directory = sys.argv[1]
    main(log_directory)
