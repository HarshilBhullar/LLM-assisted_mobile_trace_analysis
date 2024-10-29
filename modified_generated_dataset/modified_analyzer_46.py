
#!/usr/bin/python
# Filename: offline-analysis-modified.py
import os
import sys

"""
Offline analysis by replaying logs with modified metrics
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, NrRrcAnalyzer, LteRrcAnalyzer, LteMacAnalyzer

if __name__ == "__main__":

    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")
    # src.enable_log_all()

    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.JSON)  # Changed from XML to JSON
    logger.set_dump_type(MsgLogger.BOTH)  # Log to both file and console
    logger.save_decoded_msg_as("./modified_test.txt")
    logger.set_source(src)

    # # Analyzers
    nr_rrc_analyzer = NrRrcAnalyzer()
    nr_rrc_analyzer.set_source(src)  # bind with the monitor

    lte_rrc_analyzer = LteRrcAnalyzer()
    lte_rrc_analyzer.set_source(src)  # bind with the monitor

    lte_mac_analyzer = LteMacAnalyzer()
    lte_mac_analyzer.set_source(src)  # bind with the monitor

    # Additional processing: calculate average RSRP
    def calculate_average_rsrp(rsrp_list):
        if rsrp_list:
            return sum(rsrp_list) / len(rsrp_list)
        return None

    # Start the monitoring
    src.run()

    # Example of fetching and processing additional data
    rsrp_list = lte_mac_analyzer.get_rsrp_list()
    avg_rsrp = calculate_average_rsrp(rsrp_list)
    print("Average RSRP:", avg_rsrp)
