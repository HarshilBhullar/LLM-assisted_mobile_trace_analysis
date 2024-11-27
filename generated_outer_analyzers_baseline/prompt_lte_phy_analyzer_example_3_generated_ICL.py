
#!/usr/bin/python
# Filename: outer_analyzer.py

"""
Main program to analyze LTE PHY Modulation and Coding Scheme (MCS) metrics using LtePhyAnalyzer.

Author: Yuanjie Li
"""

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.analyzer import MsgLogger
from lte_phy_analyzer import LtePhyAnalyzer

def my_analysis(input_path):
    """
    Perform analysis using LtePhyAnalyzer on the given input path.

    :param input_path: Path to the directory containing LTE trace logs.
    :return: None
    """
    # Initialize OfflineReplayer as the data source
    src = OfflineReplayer()
    src.set_input_path(input_path)

    # Initialize the analyzer
    analyzer = LtePhyAnalyzer()
    analyzer.set_source(src)

    # Run analysis and handle potential errors
    try:
        src.run()
    except Exception as e:
        print("An error occurred during analysis:", e)

def main():
    # Define the path to the trace logs directory
    input_path = "path_to_trace_logs_directory"

    # Initialize the OfflineReplayer
    src = OfflineReplayer()
    src.set_input_path(input_path)

    # Enable additional logs for comprehensive analysis
    src.enable_log("LTE_PHY_PDSCH_Packet")
    src.enable_log("LTE_PHY_PUSCH_CSF")
    src.enable_log("LTE_MAC_UL_Tx_Statistics")
    src.enable_log("LTE_PHY_PUCCH_Tx_Report")
    src.enable_log("LTE_PHY_PUSCH_Tx_Report")

    # Create an instance of MsgLogger to log messages in XML format
    logger = MsgLogger()
    logger.set_source(src)
    logger.set_decode_format(MsgLogger.XML)

    # Create an instance of LtePhyAnalyzer
    analyzer = LtePhyAnalyzer()
    analyzer.set_source(src)

    # Run the analysis
    try:
        src.run()
    except Exception as e:
        print("An error occurred during the main execution:", e)

    # Calculate and save the average modulation counts to a text file
    with open("modulation_counts.txt", "w") as file:
        file.write("QPSK Count: {}\n".format(analyzer.mcs_qpsk_count))
        file.write("16QAM Count: {}\n".format(analyzer.mcs_16qam_count))
        file.write("64QAM Count: {}\n".format(analyzer.mcs_64qam_count))

if __name__ == "__main__":
    main()
