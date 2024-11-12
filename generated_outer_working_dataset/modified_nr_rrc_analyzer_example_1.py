
#!/usr/bin/python
# Filename: offline-analysis-example-modified.py
import os
import sys

"""
Modified offline analysis by replaying logs
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, \
    NrRrcAnalyzer

if __name__ == "__main__":

    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")
    # src.enable_log_all()

    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./test_modified.txt")
    logger.set_source(src)

    # Analyzers
    nr_rrc_analyzer = NrRrcAnalyzer()
    nr_rrc_analyzer.set_source(src)  # bind with the monitor

    # Additional processing or altered calculations
    def custom_processing():
        # Example: Additional logging for demonstration purposes
        print("Starting custom processing...")

        # Example: Calculate and print the total number of configured cells
        cell_list = nr_rrc_analyzer.get_cell_list()
        print(f"Total configured cells: {len(cell_list)}")

        # Example: Iterate over cell configurations and print
        for cell in cell_list:
            cell_config = nr_rrc_analyzer.get_cell_config(cell)
            if cell_config:
                print(f"Cell {cell} configuration: {cell_config.dump()}")

    # Run the modified analysis
    src.run()

    # Execute custom processing after the analysis
    custom_processing()
