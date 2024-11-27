
#!/usr/bin/python
# Filename: modified-offline-analysis-example.py
import os
import sys

"""
Offline analysis of LTE PHY Modulation and Coding Scheme (MCS) metrics
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, LtePhyAnalyzer

def my_analysis():
    try:
        # Initialize a monitor
        src = OfflineReplayer()
        src.set_input_path("./logs/")
        
        # Enable specific logs for comprehensive analysis
        src.enable_log("LTE_PHY_PDSCH_Packet")
        src.enable_log("LTE_PHY_PUSCH_CSF")
        src.enable_log("LTE_MAC_UL_Tx_Statistics")
        src.enable_log("LTE_PHY_PUCCH_Tx_Report")
        src.enable_log("LTE_PHY_PUSCH_Tx_Report")
        
        # Set up logger
        logger = MsgLogger()
        logger.set_decode_format(MsgLogger.XML)
        logger.set_dump_type(MsgLogger.FILE_ONLY)
        logger.save_decoded_msg_as("./modulation_counts.txt")
        logger.set_source(src)

        # Attach the custom analyzer
        lte_phy_analyzer = LtePhyAnalyzer()
        lte_phy_analyzer.set_source(src)

        # Run the analysis
        src.run()

        # Calculate and save the average modulation counts
        with open("modulation_counts.txt", "a") as f:
            f.write(f"QPSK Count: {lte_phy_analyzer.mcs_qpsk_count}\n")
            f.write(f"16QAM Count: {lte_phy_analyzer.mcs_16qam_count}\n")
            f.write(f"64QAM Count: {lte_phy_analyzer.mcs_64qam_count}\n")

    except Exception as e:
        print(f"An error occurred during analysis: {e}")

if __name__ == "__main__":
    my_analysis()
