
#!/usr/bin/python
# Filename: modified-offline-analysis-example.py
import os
import sys

"""
Modified offline analysis by replaying logs with additional metrics.
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
    logger.save_decoded_msg_as("./test_modified.txt")  # Changed output file name
    logger.set_source(src)

    umts_nas_analyzer = UmtsNasAnalyzer()
    umts_nas_analyzer.set_source(src)

    # Additional analysis: calculating average delay class from NAS messages
    def calculate_average_delay_class():
        delay_classes = []

        def callback(msg):
            if msg.type_id == "UMTS_NAS_MM_State":
                delay_class = msg.data.get("delay_class")
                if delay_class is not None:
                    delay_classes.append(int(delay_class))

        umts_nas_analyzer.add_source_callback(callback)

        src.run()

        if delay_classes:
            avg_delay_class = sum(delay_classes) / len(delay_classes)
            print(f"Average Delay Class: {avg_delay_class}")
        else:
            print("No delay class information available.")

    # Start the modified monitoring
    calculate_average_delay_class()
