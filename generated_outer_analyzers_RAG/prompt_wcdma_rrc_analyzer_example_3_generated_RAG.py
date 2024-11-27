
#!/usr/bin/python
# Filename: modified-offline-analysis-example.py

import os
import sys

"""
Modified offline analysis by replaying logs with RRC state duration calculation.
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, WcdmaRrcAnalyzer

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

    wcdma_rrc_analyzer = WcdmaRrcAnalyzer()
    wcdma_rrc_analyzer.set_source(src)

    # Custom analysis: Calculate duration in each RRC state
    state_durations = {}
    message_count = 0

    def custom_rrc_state_callback(msg):
        nonlocal message_count
        if msg.type_id == "WCDMA_RRC_States":
            state = str(msg.data['RRC State'])
            state_durations[state] = state_durations.get(state, 0) + 1
            message_count += 1

            if message_count % 100 == 0:
                print("Current RRC State Durations:", state_durations)

    wcdma_rrc_analyzer.add_source_callback(custom_rrc_state_callback)

    # Start the monitoring
    src.run()
