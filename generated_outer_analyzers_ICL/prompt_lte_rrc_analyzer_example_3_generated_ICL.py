
#!/usr/bin/python
# Filename: modified-lte-rrc-analysis.py
import os
import sys

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger
from lte_rrc_analyzer import LteRrcAnalyzer

"""
Modified LTE RRC analysis script for offline log replay
"""

def calculate_additional_metrics(event):
    log_item = event.data
    if event.type_id == "LTE_RRC_OTA_Packet":
        rsrp = log_item.get('lte-rrc.rsrpResult')
        rsrq = log_item.get('lte-rrc.rsrqResult')
        if rsrp is not None and rsrq is not None:
            sinr = rsrp - rsrq
            print(f"SINR calculated: {sinr}")

if __name__ == "__main__":

    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")

    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./test_modified.txt")
    logger.set_source(src)

    lte_rrc_analyzer = LteRrcAnalyzer()
    lte_rrc_analyzer.set_source(src)

    src.add_callback("LTE_RRC_OTA_Packet", calculate_additional_metrics)

    # Start the monitoring
    src.run()
