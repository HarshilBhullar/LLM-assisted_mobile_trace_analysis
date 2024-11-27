
#!/usr/bin/python
# Filename: track_cell_info_analyzer_outer.py

"""
A script to execute the TrackCellInfoAnalyzer for LTE RRC analysis.

Author: Yuanjie Li, Zhehui Zhang
"""

import sys
from mobile_insight.analyzer.analyzer import OfflineReplayer
from mobile_insight.analyzer.msglogger import MsgLogger
from mobile_insight.analyzer.track_cell_info_analyzer import TrackCellInfoAnalyzer
from mobile_insight.monitor import OfflineReplayer

def modified_offline_analysis(input_path, output_file):
    """
    Perform offline analysis using TrackCellInfoAnalyzer.

    :param input_path: Directory containing the log files.
    :type input_path: str
    :param output_file: Path to save the decoded messages.
    :type output_file: str
    """
    # Initialize offline replayer
    src = OfflineReplayer()
    src.set_input_path(input_path)

    # Enable various logs
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    # Initialize and set up MsgLogger
    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.JSON)
    logger.set_source(src)
    logger.set_output_path(output_file)

    # Set up TrackCellInfoAnalyzer
    analyzer = TrackCellInfoAnalyzer()
    analyzer.set_source(src)

    # Calculate average downlink frequency
    def calculate_average_dl_frequency():
        dl_frequencies = []
        for msg in analyzer.get_decoded_messages("LTE_RRC_Serv_Cell_Info"):
            dl_frequencies.append(msg['Downlink frequency'])

        if dl_frequencies:
            average_dl_freq = sum(dl_frequencies) / len(dl_frequencies)
            print(f"Average Downlink Frequency: {average_dl_freq} MHz")

    # Run the source to replay logs and execute analysis
    try:
        src.run()
        calculate_average_dl_frequency()
    except Exception as e:
        print(f"An error occurred during analysis: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python track_cell_info_analyzer_outer.py <input_path> <output_file>")
    else:
        input_path = sys.argv[1]
        output_file = sys.argv[2]
        modified_offline_analysis(input_path, output_file)
