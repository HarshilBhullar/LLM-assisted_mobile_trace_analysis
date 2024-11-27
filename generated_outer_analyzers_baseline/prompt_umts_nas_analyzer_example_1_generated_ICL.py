
#!/usr/bin/python
# Filename: outer_umts_nas_analyzer.py

"""
Outer Analyzer for UMTS NAS layer

Author: Your Name
Date: Today's date
"""

import sys
from mobile_insight.analyzer import OfflineReplayer
from umts_nas_analyzer import UmtsNasAnalyzer  # Assuming UmtsNasAnalyzer is in a file named umts_nas_analyzer.py

def calculate_average_delay_class(log_file_path, output_file_path):
    """
    Calculate the average delay class from UMTS NAS messages.

    :param log_file_path: Path to the input log file.
    :param output_file_path: Path to the output text file to save decoded messages.
    """
    # Initialize OfflineReplayer
    replayer = OfflineReplayer()
    replayer.set_input_path(log_file_path)

    # Initialize UMTS NAS Analyzer
    nas_analyzer = UmtsNasAnalyzer()
    nas_analyzer.set_source(replayer)

    # Store delay classes
    delay_classes = []

    # Define callback to capture delay class
    def nas_callback(nas_message):
        if 'delay_class' in nas_message.data:
            delay_classes.append(int(nas_message.data['delay_class']))

    nas_analyzer.add_callback(nas_callback)

    # Enable logs for LTE and 5G if needed
    replayer.enable_log("LTE_NAS_EMM_State")
    replayer.enable_log("NRMM_State")

    try:
        # Run the OfflineReplayer
        replayer.run()

        # Calculate average delay class
        if delay_classes:
            avg_delay_class = sum(delay_classes) / len(delay_classes)
        else:
            avg_delay_class = 0

        # Print the result
        print(f"Average Delay Class: {avg_delay_class}")

        # Save decoded messages to a text file
        with open(output_file_path, 'w') as output_file:
            for msg in delay_classes:
                output_file.write(f"{msg}\n")

    except Exception as e:
        print(f"An error occurred during execution: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python outer_umts_nas_analyzer.py <log_file_path> <output_file_path>")
    else:
        log_file_path = sys.argv[1]
        output_file_path = sys.argv[2]
        calculate_average_delay_class(log_file_path, output_file_path)
