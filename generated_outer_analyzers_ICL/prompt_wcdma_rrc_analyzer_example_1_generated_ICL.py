
#!/usr/bin/python
# Filename: offline-wcdma-analysis.py

import os
import sys
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, WcdmaRrcAnalyzer

def main(input_path, output_file):
    try:
        # Initialize a monitor
        src = OfflineReplayer()
        src.set_input_path(input_path)

        # Enable relevant logs
        src.enable_log("WCDMA_RRC_OTA_Packet")
        src.enable_log("WCDMA_RRC_Serv_Cell_Info")
        src.enable_log("WCDMA_RRC_States")

        # Set up the logger
        logger = MsgLogger()
        logger.set_decode_format(MsgLogger.XML)
        logger.set_dump_type(MsgLogger.FILE_ONLY)
        logger.save_decoded_msg_as(output_file)
        logger.set_source(src)

        # Set up the analyzer
        wcdma_rrc_analyzer = WcdmaRrcAnalyzer()
        wcdma_rrc_analyzer.set_source(src)

        # Start the monitoring
        src.run()

        # Retrieve and print cell information
        cell_list = wcdma_rrc_analyzer.get_cell_list()
        for cell in cell_list:
            config = wcdma_rrc_analyzer.get_cell_config(cell)
            if config:
                print(f"Cell ID: {cell[0]}, Frequency: {cell[1]}")
                print("Configuration Details:")
                print(config.dump())

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: offline-wcdma-analysis.py <input_path> <output_file>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_file = sys.argv[2]
    main(input_path, output_file)
