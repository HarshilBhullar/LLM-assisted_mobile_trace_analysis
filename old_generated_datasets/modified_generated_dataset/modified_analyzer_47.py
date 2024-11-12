
#!/usr/bin/python
# Filename: offline-analysis-modified.py
import os
import sys

"""
Offline analysis with modified processing
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, NrRrcAnalyzer, LteRrcAnalyzer, LteNasAnalyzer, LteMacAnalyzer

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

    # Analyzers
    nr_rrc_analyzer = NrRrcAnalyzer()
    nr_rrc_analyzer.set_source(src)  # bind with the monitor
    nr_rrc_analyzer.set_analysis_mode(NrRrcAnalyzer.DETAILED)  # Example change: use detailed mode

    lte_rrc_analyzer = LteRrcAnalyzer()
    lte_rrc_analyzer.set_source(src)  # bind with the monitor

    # Additional analyzers with modified settings
    lte_nas_analyzer = LteNasAnalyzer()
    lte_nas_analyzer.set_source(src)
    lte_nas_analyzer.set_analysis_mode(LteNasAnalyzer.SIMPLE)  # Example change: use simple mode

    lte_mac_analyzer = LteMacAnalyzer()
    lte_mac_analyzer.set_source(src)
    lte_mac_analyzer.adjust_metric_threshold(10)  # Example change: adjust metric threshold

    # Start the monitoring with modified analyzers
    src.run()
