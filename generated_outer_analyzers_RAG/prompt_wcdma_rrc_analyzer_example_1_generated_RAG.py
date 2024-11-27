
#!/usr/bin/python
# Filename: modified-offline-analysis-example.py
import os
import sys
import traceback

"""
Modified offline analysis by replaying logs
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, WcdmaRrcAnalyzer

def main(input_path, output_file):
    try:
        # Initialize a monitor
        src = OfflineReplayer()
        src.set_input_path(input_path)
        # src.enable_log_all()

        src.enable_log("LTE_PHY_Serv_Cell_Measurement")
        src.enable_log("5G_NR_RRC_OTA_Packet")
        src.enable_log("LTE_RRC_OTA_Packet")
        src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

        logger = MsgLogger()
        logger.set_decode_format(MsgLogger.XML)
        logger.set_dump_type(MsgLogger.FILE_ONLY)
        logger.save_decoded_msg_as(output_file)
        logger.set_source(src)

        wcdma_rrc_analyzer = WcdmaRrcAnalyzer()
        wcdma_rrc_analyzer.set_source(src)

        # Start the monitoring
        src.run()

        # Fetch and print cell configurations
        cell_list = wcdma_rrc_analyzer.get_cell_list()
        for cell in cell_list:
            config = wcdma_rrc_analyzer.get_cell_config(cell)
            if config:
                print(f"Cell ID: {cell[0]}, Frequency: {cell[1]}")
                print(f"Configuration: {config.dump()}")
    except Exception as e:
        print("An error occurred:", str(e))
        traceback.print_exc()

if __name__ == "__main__":
    # Use command line arguments for input and output paths
    input_path = sys.argv[1] if len(sys.argv) > 1 else "./logs/"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "./modified_test.txt"

    main(input_path, output_file)
