
#!/usr/bin/python
# Filename: modified-offline-analysis-example.py
import os
import sys

"""
Offline analysis by replaying logs
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, MmAnalyzer

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

    mm_analyzer = MmAnalyzer()
    mm_analyzer.set_source(src)

    # Example of additional metric: Count of LTE attach attempts
    attach_attempts = 0

    def custom_callback(event):
        nonlocal attach_attempts
        log_item = event.data.decode()
        if "nas_eps.nas_msg_emm_type" in log_item and "Attach request" in log_item:
            attach_attempts += 1

    src.add_callback("LTE_NAS_EMM_Plain_OTA_Incoming_Packet", custom_callback)

    # Start the monitoring
    src.run()

    print(f"LTE Attach Attempts: {attach_attempts}")
