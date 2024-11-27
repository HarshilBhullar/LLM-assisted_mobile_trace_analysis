
#!/usr/bin/python
# Filename: outer_wcdma_rrc_analyzer.py

"""
Outer script for WCDMA RRC analyzer utilizing MobileInsight library.

Author: AI Assistant
"""

import sys
import argparse
from mobile_insight.analyzer import WcdmaRrcAnalyzer
from mobile_insight.monitor import OfflineReplayer, MsgLogger

def main(input_path, output_file):
    # Initialize OfflineReplayer as data source
    src = OfflineReplayer()
    src.set_input_path(input_path)

    # Setup MsgLogger
    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.save_decoded_msg_as(output_file)
    logger.set_source(src)

    # Initialize WcdmaRrcAnalyzer
    analyzer = WcdmaRrcAnalyzer()
    analyzer.set_source(src)

    # Enable relevant logs
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    # Run analysis
    try:
        src.run()

        # Retrieve and print cell information
        cell_list = analyzer.get_cell_list()
        for cell in cell_list:
            config = analyzer.get_cell_config(cell)
            if config:
                print(f"Cell ID: {cell[0]}, Frequency: {cell[1]}, Configuration: {config.dump()}")
    except Exception as e:
        print(f"An error occurred during analysis: {e}")

if __name__ == "__main__":
    # Command-line argument parsing
    parser = argparse.ArgumentParser(description='Perform offline analysis on WCDMA RRC logs.')
    parser.add_argument('--input_path', type=str, required=True, help='Path to the directory containing log files.')
    parser.add_argument('--output_file', type=str, default='modified_test.txt', help='File to save decoded messages.')

    args = parser.parse_args()

    main(args.input_path, args.output_file)
