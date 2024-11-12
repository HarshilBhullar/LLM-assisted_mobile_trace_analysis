
#!/usr/bin/python
# Filename: offline-analysis-modified.py
import os
import sys

"""
Offline analysis by replaying logs with modified metrics
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, LteRlcAnalyzer

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

    lte_rlc_analyzer = LteRlcAnalyzer()
    lte_rlc_analyzer.set_source(src)

    # Modified calculation or metrics
    # Here we can add modifications like adjusting the log file or adding new metrics
    # For example, let's add a simple print statement to indicate start of analysis
    print("Starting modified offline analysis...")

    # Start the monitoring
    src.run()
