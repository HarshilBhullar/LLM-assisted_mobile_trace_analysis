
#!/usr/bin/python
# Filename: modified-offline-analysis-example.py
import os
import sys

"""
Modified offline analysis by replaying logs
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

    # Custom callback to track LTE attach attempts
    attach_attempts = 0

    def custom_callback(event):
        global attach_attempts
        log_item = event.data.decode()
        decoded_event = Event(event.timestamp, event.type_id, log_item)

        if event.type_id.startswith("LTE_NAS_EMM_Plain_OTA_"):
            for proto in decoded_event.data.iter('proto'):
                if proto.get('name') == "gsm_a.dtap":
                    raw_state_name = proto.get('showname')
                    if "Attach request" in raw_state_name:
                        attach_attempts += 1
                        print(f"Attach request detected. Total attempts: {attach_attempts}")

    src.add_source_callback(custom_callback, "LTE_NAS_EMM_Plain_OTA_Incoming_Packet")

    # Start the monitoring
    try:
        src.run()
    except Exception as e:
        print(f"An error occurred during the replay: {e}")

    # Output the calculated metrics
    print(f"Total LTE attach attempts: {attach_attempts}")
