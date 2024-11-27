
#!/usr/bin/python
# Filename: wcdma_rrc_outer_analyzer.py

import os
import sys

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, WcdmaRrcAnalyzer

def custom_rrc_state_callback(msg, rrc_state_durations, state_change_count):
    rrc_state = msg['RRC State']
    state_change_count += 1
    if rrc_state not in rrc_state_durations:
        rrc_state_durations[rrc_state] = 0
    rrc_state_durations[rrc_state] += 1

    if state_change_count % 100 == 0:
        print("Cumulative RRC state durations:")
        for state, duration in rrc_state_durations.items():
            print(f"State {state}: {duration} messages")

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
    logger.save_decoded_msg_as("./modified_test.txt")
    logger.set_source(src)

    # Analyzer
    wcdma_rrc_analyzer = WcdmaRrcAnalyzer()
    wcdma_rrc_analyzer.set_source(src)  # bind with the monitor

    # Custom RRC state analysis
    rrc_state_durations = {}
    state_change_count = 0

    def rrc_state_callback(msg):
        nonlocal state_change_count
        custom_rrc_state_callback(msg, rrc_state_durations, state_change_count)
        state_change_count += 1

    # Override the default RRC state callback
    wcdma_rrc_analyzer.__callback_rrc_state = rrc_state_callback

    # Execute the replay of logs
    src.run()
