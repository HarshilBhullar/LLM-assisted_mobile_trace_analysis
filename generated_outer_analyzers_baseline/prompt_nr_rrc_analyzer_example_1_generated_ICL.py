
#!/usr/bin/python
# Filename: nr_rrc_outer_analyzer.py
"""
Outer analyzer for NR RRC analysis.
Author: Qianru Li
"""

import os
import sys
from mobile_insight.monitor import OfflineReplayer
from nr_rrc_analyzer import NrRrcAnalyzer

def main(log_directory):
    try:
        # Initialize the OfflineReplayer
        src = OfflineReplayer()
        src.set_input_path(log_directory)

        # Instantiate the NrRrcAnalyzer
        analyzer = NrRrcAnalyzer()
        analyzer.set_source(src)

        # Run the analysis
        src.run()

        # Execute custom processing
        process_results(analyzer)

    except Exception as e:
        print(f"An error occurred: {e}")

def process_results(analyzer):
    try:
        # Calculate and print the total number of configured cells
        configured_cells = analyzer.get_cell_list()
        print(f"Total number of configured cells: {len(configured_cells)}")

        # Iterate over each cell configuration and log the details
        for cell in configured_cells:
            cell_config = analyzer.get_cell_config(cell)
            if cell_config:
                print(f"Cell configuration for cell {cell}:")
                print(cell_config.dump())

    except Exception as e:
        print(f"Error during custom processing: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python nr_rrc_outer_analyzer.py <log_directory>")
    else:
        log_directory = sys.argv[1]
        if not os.path.exists(log_directory):
            print(f"Error: Log directory {log_directory} does not exist.")
        else:
            main(log_directory)
