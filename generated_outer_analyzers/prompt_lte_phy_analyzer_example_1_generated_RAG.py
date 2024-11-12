
#!/usr/bin/python

import sys

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, LtePhyAnalyzer

if __name__ == "__main__":

    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")

    # Enable logs relevant for analysis
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    # Set up message logging
    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./phy_analysis_output.txt")
    logger.set_source(src)

    # Set up the LTE PHY Analyzer
    lte_phy_analyzer = LtePhyAnalyzer()
    lte_phy_analyzer.set_source(src)

    # Start the monitoring
    src.run()

    # Calculate additional metrics
    # Assuming the LtePhyAnalyzer class provides methods to get total bandwidth and timestamps
    total_dl_bandwidth = lte_phy_analyzer.lte_dl_bw
    total_time_seconds = (lte_phy_analyzer.prev_timestamp_dl - lte_phy_analyzer.init_timestamp).total_seconds()

    if total_time_seconds > 0:
        avg_dl_bandwidth = total_dl_bandwidth / (total_time_seconds * 1000000.0)  # Convert to Mbps
        print(f"Average Downlink Bandwidth: {avg_dl_bandwidth:.2f} Mbps")
    else:
        print("Insufficient data for average bandwidth calculation.")
