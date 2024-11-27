
#!/usr/bin/python
# Filename: offline-rrc-analysis.py
import sys
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import LteRrcAnalyzer

def main(log_dir):
    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path(log_dir)

    # Initialize LteRrcAnalyzer
    lte_rrc_analyzer = LteRrcAnalyzer()
    lte_rrc_analyzer.set_source(src)

    # Set up a callback for RSRP measurements
    rsrp_values = []

    def rsrp_callback(event):
        if event.type == 'rsrp':
            rsrp_values.append(event.data)

    lte_rrc_analyzer.add_event_callback('rsrp', rsrp_callback)

    # Run the analyzer
    src.run()

    # Calculate average RSRP
    if rsrp_values:
        avg_rsrp = sum(rsrp_values) / len(rsrp_values)
        print(f"Average RSRP: {avg_rsrp:.2f} dBm")
    else:
        print("No RSRP measurements found.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python offline-rrc-analysis.py [log_directory]")
        sys.exit(1)
    
    log_directory = sys.argv[1]
    main(log_directory)
