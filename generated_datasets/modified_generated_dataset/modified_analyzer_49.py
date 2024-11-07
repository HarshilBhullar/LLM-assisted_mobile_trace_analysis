
#!/usr/bin/python
# Filename: offline-analysis-modified.py
import os
import sys

"""
Modified offline analysis by replaying logs with adjusted metrics
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, NrRrcAnalyzer, LteRrcAnalyzer, LteMeasurementAnalyzer

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
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./modified_test.txt")
    logger.set_source(src)

    # # Analyzers
    nr_rrc_analyzer = NrRrcAnalyzer()
    nr_rrc_analyzer.set_source(src)  # bind with the monitor

    lte_rrc_analyzer = LteRrcAnalyzer()
    lte_rrc_analyzer.set_source(src)  # bind with the monitor

    lte_meas_analyzer = LteMeasurementAnalyzer()
    lte_meas_analyzer.set_source(src)

    # Adjusted processing: Calculate average RSRP
    def calculate_average_rsrp(rsrp_list):
        if not rsrp_list:
            return None
        return sum(rsrp_list) / len(rsrp_list)

    # Get and print the adjusted metrics
    rsrp_list = lte_meas_analyzer.get_rsrp_list()
    average_rsrp = calculate_average_rsrp(rsrp_list)
    if average_rsrp is not None:
        print(f"Average RSRP: {average_rsrp}")
    else:
        print("No RSRP data available.")

    # Start the monitoring
    src.run()
