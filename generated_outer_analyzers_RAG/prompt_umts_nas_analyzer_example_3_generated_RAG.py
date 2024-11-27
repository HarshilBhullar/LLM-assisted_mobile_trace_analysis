
#!/usr/bin/python
# Filename: modified-offline-analysis-example.py
import os
import sys

"""
Offline analysis by replaying logs with custom UMTS NAS layer processing
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, UmtsNasAnalyzer

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

    umts_nas_analyzer = UmtsNasAnalyzer()
    umts_nas_analyzer.set_source(src)

    # Define custom message processing function
    def custom_processing(msg):
        if msg.type_id == "UMTS_NAS_MM_State":
            log_item = msg.data.decode()
            if "MM State" in log_item:
                print(f"Custom Log - MM State: {log_item['MM State']} at {log_item['timestamp']}")

    # Register custom processing function
    umts_nas_analyzer.add_callback("UMTS_NAS_MM_State", custom_processing)

    # Start the monitoring
    src.run()
