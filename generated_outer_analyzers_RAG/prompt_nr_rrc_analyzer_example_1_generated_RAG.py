
#!/usr/bin/python
# Filename: offline-analysis-nr-rrc-example.py
import os
import sys

"""
Offline analysis by replaying NR RRC logs
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, NrRrcAnalyzer

if __name__ == "__main__":

    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")
    # src.enable_log_all()

    # Enable relevant NR RRC logs
    src.enable_log("5G_NR_RRC_OTA_Packet")

    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./nr_rrc_analysis_output.txt")
    logger.set_source(src)

    nr_rrc_analyzer = NrRrcAnalyzer()
    nr_rrc_analyzer.set_source(src)

    # Start the monitoring
    src.run()

    # Example custom processing: Calculate and log the number of configured cells
    def log_configured_cells():
        cell_list = nr_rrc_analyzer.get_cell_list()
        print(f"Total number of configured cells: {len(cell_list)}")
        for cell in cell_list:
            config = nr_rrc_analyzer.get_cell_config(cell)
            if config:
                print(f"Cell {cell}: {config.dump()}")
            else:
                print(f"Cell {cell}: No configuration available.")

    # Execute custom processing after analysis
    log_configured_cells()
