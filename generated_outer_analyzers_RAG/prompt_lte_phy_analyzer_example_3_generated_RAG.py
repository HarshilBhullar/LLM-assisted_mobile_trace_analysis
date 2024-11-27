
#!/usr/bin/python
# Filename: my_analysis.py

import os
import sys

"""
Analysis of 4G PHY Modulation and Coding Scheme (MCS) metrics
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, LtePhyAnalyzer

if __name__ == "__main__":

    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")

    src.enable_log("LTE_PHY_PDSCH_Packet")
    src.enable_log("LTE_PHY_PUSCH_CSF")
    src.enable_log("LTE_MAC_UL_Tx_Statistics")
    src.enable_log("LTE_PHY_PUCCH_Tx_Report")
    src.enable_log("LTE_PHY_PUSCH_Tx_Report")

    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./phy_analysis.txt")
    logger.set_source(src)

    lte_phy_analyzer = LtePhyAnalyzer()
    lte_phy_analyzer.set_source(src)

    # Start the monitoring
    try:
        src.run()

        # Calculate modulation counts
        with open("modulation_counts.txt", "w") as f:
            mcs_qpsk_count = lte_phy_analyzer.mcs_qpsk_count
            mcs_16qam_count = lte_phy_analyzer.mcs_16qam_count
            mcs_64qam_count = lte_phy_analyzer.mcs_64qam_count

            f.write(f"QPSK Count: {mcs_qpsk_count}\n")
            f.write(f"16QAM Count: {mcs_16qam_count}\n")
            f.write(f"64QAM Count: {mcs_64qam_count}\n")

    except Exception as e:
        print(f"An error occurred during the analysis: {str(e)}")
