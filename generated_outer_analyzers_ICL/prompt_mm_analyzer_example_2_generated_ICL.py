
#!/usr/bin/python
# Filename: modified-mm-analyzer-example.py

import os
import sys

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger
from mm_analyzer import MmAnalyzer

"""
This example shows how to perform modified offline analysis using MmAnalyzer
"""

def custom_callback(event):
    log_item = event.data.decode()
    if event.type_id == "LTE_NAS_EMM_Plain_OTA_Incoming_Packet":
        # Check for LTE attach attempts
        nas_type = ""
        if "msg_emm_type" in log_item:
            nas_type = log_item["msg_emm_type"]
        if nas_type == "Attach request":
            custom_metrics["lte_attach_attempts"] += 1

if __name__ == "__main__":
    custom_metrics = {"lte_attach_attempts": 0}

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
    logger.save_decoded_msg_as("./modified_test.txt")
    logger.set_source(src)

    mm_analyzer = MmAnalyzer()
    mm_analyzer.set_source(src)

    # Register custom callback for specific message type
    src.add_callback("LTE_NAS_EMM_Plain_OTA_Incoming_Packet", custom_callback)

    # Start the monitoring
    try:
        src.run()
    except Exception as e:
        print(f"Error during log replay: {e}")

    # Output the custom metric
    print(f"Number of LTE attach attempts: {custom_metrics['lte_attach_attempts']}")
