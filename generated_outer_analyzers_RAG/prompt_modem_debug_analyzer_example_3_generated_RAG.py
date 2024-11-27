
#!/usr/bin/python
# Filename: modem-debug-analyzer-outer.py
import os
import sys

"""
Outer analyzer script using ModemDebugAnalyzer for cellular log processing
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger
from modem_debug_analyzer import ModemDebugAnalyzer

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

    modem_debug_analyzer = ModemDebugAnalyzer()
    modem_debug_analyzer.set_source(src)

    # New functionality: Enable additional log for analysis
    src.enable_log("LTE_PHY_PDSCH_Stat_Indication")

    # Start the monitoring
    src.run()
