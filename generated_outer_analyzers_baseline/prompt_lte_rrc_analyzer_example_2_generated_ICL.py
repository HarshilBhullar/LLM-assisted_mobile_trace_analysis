
#!/usr/bin/python
# Filename: lte_rrc_analyzer_main.py

"""
Main script to execute LTE RRC Analyzer.
"""

import sys
import os
from mobile_insight.analyzer import OfflineReplayer
from lte_rrc_analyzer import LteRrcAnalyzer

def main(log_dir):
    """
    Main function to run the LTE RRC Analyzer.

    :param log_dir: The directory containing log files to be analyzed.
    :type log_dir: str
    """
    try:
        if not os.path.exists(log_dir):
            raise FileNotFoundError(f"Log directory {log_dir} does not exist")

        # Initialize the data source
        src = OfflineReplayer()
        src.set_input_path(log_dir)

        # Initialize the LTE RRC Analyzer
        analyzer = LteRrcAnalyzer()
        analyzer.set_source(src)

        # Callback to process and log average RSRP
        def rsrp_callback(event):
            rsrp_values = []

            def rsrp_handler(evt):
                if evt.type_id == 'rsrp':
                    rsrp_values.append(int(evt.data))

            analyzer.add_callback(rsrp_handler)

            # Start replaying logs
            src.run()

            if rsrp_values:
                avg_rsrp = sum(rsrp_values) / len(rsrp_values)
                print(f"Average RSRP: {avg_rsrp:.2f}")

        analyzer.add_callback(rsrp_callback)
        src.run()

    except Exception as e:
        print(f"An error occurred during analysis: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python lte_rrc_analyzer_main.py <log_directory>")
        sys.exit(1)

    log_directory = sys.argv[1]
    main(log_directory)
