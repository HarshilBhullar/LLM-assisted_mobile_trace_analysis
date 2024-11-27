
#!/usr/bin/python
# Filename: lte_rrc_analysis.py

import os
import sys

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.lte_rrc_analyzer import LteRrcAnalyzer

def average_rsrp_callback(analyzer):
    rsrp_values = []
    
    def on_rsrp_received(event):
        if event.type_id == 'rsrp':
            rsrp_values.append(event.data)
    
    analyzer.add_callback(on_rsrp_received)
    
    def calculate_average_rsrp():
        if rsrp_values:
            average_rsrp = sum(rsrp_values) / len(rsrp_values)
            print(f"Average RSRP: {average_rsrp} dBm")
    
    return calculate_average_rsrp

if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print("Usage: python lte_rrc_analysis.py <log_directory>")
        sys.exit(1)
    
    log_directory = sys.argv[1]
    
    try:
        # Initialize the source
        src = OfflineReplayer()
        src.set_input_path(log_directory)
        
        # Initialize and configure the analyzer
        lte_rrc_analyzer = LteRrcAnalyzer()
        lte_rrc_analyzer.set_source(src)
        
        # Setup RSRP analysis
        calculate_average_rsrp = average_rsrp_callback(lte_rrc_analyzer)
        
        # Start the monitoring
        src.run()
        
        # Calculate and display the average RSRP
        calculate_average_rsrp()
    
    except Exception as e:
        print(f"An error occurred during the analysis: {e}")
        sys.exit(1)
