
#!/usr/bin/python
# Filename: track_cell_info_analyzer_example.py

import os
import sys

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.track_cell_info_analyzer import TrackCellInfoAnalyzer

"""
This example demonstrates how to use the TrackCellInfoAnalyzer to process LTE RRC messages
and track cell information such as downlink frequency, uplink bandwidth, and operator details.
"""

def analyze_cell_info(input_path):
    # Initialize a 3G/4G monitor
    src = OfflineReplayer()
    src.set_input_path(input_path)

    # Initialize the TrackCellInfoAnalyzer
    cell_info_analyzer = TrackCellInfoAnalyzer()
    cell_info_analyzer.set_source(src)

    # Enable specific logs for LTE RRC messages
    src.enable_log("LTE_RRC_Serv_Cell_Info")
    src.enable_log("LTE_RRC_MIB_Packet")

    # Start the monitoring
    src.run()

    # Calculate and print additional metrics
    total_bandwidth = (cell_info_analyzer.get_cur_downlink_bandwidth() + 
                       cell_info_analyzer.get_cur_uplink_bandwidth())
    print(f"Total Bandwidth: {total_bandwidth}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python track_cell_info_analyzer_example.py [input_path]")
        sys.exit(1)

    input_path = sys.argv[1]
    analyze_cell_info(input_path)
