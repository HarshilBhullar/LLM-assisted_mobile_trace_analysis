
#!/usr/bin/python
# Filename: umts_nas_analysis.py

import os
import sys

"""
UMTS NAS layer analysis by replaying logs
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, UmtsNasAnalyzer

if __name__ == "__main__":

    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")
    
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    # Setup logger
    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./umts_nas_log.txt")
    logger.set_source(src)

    # Setup analyzer
    umts_nas_analyzer = UmtsNasAnalyzer()
    umts_nas_analyzer.set_source(src)

    # Custom message processing
    def custom_processing(msg):
        if msg.type_id == "UMTS_NAS_MM_State" and "MM State" in msg.data:
            print(f"Custom Log: MM State - {msg.data['MM State']}")

    # Add custom callback to the analyzer
    umts_nas_analyzer.add_source_callback(custom_processing)

    # Start the monitoring
    src.run()
