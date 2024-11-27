
#!/usr/bin/python
# Filename: modified-lte-phy-analysis.py

import os
import sys

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, LtePhyAnalyzer

if __name__ == "__main__":

    # Initialize a 3G/4G monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")

    # Enable necessary logs
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    # Initialize LTE PHY Analyzer
    phy_analyzer = LtePhyAnalyzer()
    phy_analyzer.set_source(src)

    # Initialize a message logger
    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./lte_phy_analysis_logs.xml")
    logger.set_source(src)

    # Start replaying logs and running analysis
    src.run()

    # Calculate additional metrics
    total_downlink_bandwidth = 0.0
    total_time = 0.0

    for msg in src.get_messages():
        if msg.type_id == "LTE_PHY_PDSCH_Packet":
            log_item = msg.data.decode()
            if "timestamp" in log_item:
                if not hasattr(phy_analyzer, 'start_time'):
                    phy_analyzer.start_time = log_item['timestamp']
                total_time = (log_item['timestamp'] - phy_analyzer.start_time).total_seconds()
                total_downlink_bandwidth += phy_analyzer.lte_dl_bw

    avg_downlink_bandwidth = total_downlink_bandwidth / total_time if total_time > 0 else 0
    print(f"Average Downlink Bandwidth: {avg_downlink_bandwidth:.2f} Mbps")
