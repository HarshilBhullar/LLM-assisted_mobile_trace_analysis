
#!/usr/bin/python
# Filename: nr_rrc_analysis.py

import os
import sys
import traceback

"""
NR RRC analysis by replaying logs
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import NrRrcAnalyzer

if __name__ == "__main__":

    try:
        # Initialize a monitor
        src = OfflineReplayer()
        src.set_input_path("./logs/")

        # Enable necessary NR RRC logs
        src.enable_log("5G_NR_RRC_OTA_Packet")

        # Initialize the NR RRC Analyzer
        nr_rrc_analyzer = NrRrcAnalyzer()
        nr_rrc_analyzer.set_source(src)

        # Start the monitoring
        src.run()

        # Custom processing: Extract specific metrics
        cell_list = nr_rrc_analyzer.get_cell_list()
        print(f"Total number of configured cells: {len(cell_list)}")
        for cell in cell_list:
            cell_config = nr_rrc_analyzer.get_cell_config(cell)
            if cell_config:
                print(f"Cell Configuration for {cell}:")
                print(cell_config.dump())

    except Exception as e:
        print("An error occurred during the NR RRC analysis:")
        print(traceback.format_exc())
