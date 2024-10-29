
#!/usr/bin/python
# Filename: offline-analysis-modified.py
import os
import sys

"""
Modified offline analysis by replaying logs
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, NrRrcAnalyzer, LteRrcAnalyzer, WcdmaRrcAnalyzer, LteNasAnalyzer, UmtsNasAnalyzer, LteMacAnalyzer, LteMeasurementAnalyzer

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

    # Modified Analyzers
    nr_rrc_analyzer = NrRrcAnalyzer()
    nr_rrc_analyzer.set_source(src)  # bind with the monitor

    lte_rrc_analyzer = LteRrcAnalyzer()
    lte_rrc_analyzer.set_source(src)  # bind with the monitor

    # Adding a new analyzer
    lte_nas_analyzer = LteNasAnalyzer()
    lte_nas_analyzer.set_source(src)

    # Applying a different calculation to LTE Measurement Analyzer
    lte_meas_analyzer = LteMeasurementAnalyzer()
    lte_meas_analyzer.set_source(src)

    # Calculate and print average RSRP
    rsrp_list = lte_meas_analyzer.get_rsrp_list()
    if rsrp_list:
        avg_rsrp = sum(rsrp_list) / len(rsrp_list)
        print(f"Average RSRP: {avg_rsrp}")

    # Calculate and print average RSRQ
    rsrq_list = lte_meas_analyzer.get_rsrq_list()
    if rsrq_list:
        avg_rsrq = sum(rsrq_list) / len(rsrq_list)
        print(f"Average RSRQ: {avg_rsrq}")

    # Start the monitoring
    src.run()
