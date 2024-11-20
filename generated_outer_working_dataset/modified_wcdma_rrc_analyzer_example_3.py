
#!/usr/bin/python
# Filename: offline-analysis-modified.py
import os
import sys

"""
Modified offline analysis by replaying logs
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
    logger.save_decoded_msg_as("./modified_test.txt")  # Changed output file name
    logger.set_source(src)

    wcdma_rrc_analyzer = WcdmaRrcAnalyzer()
    wcdma_rrc_analyzer.set_source(src)  # bind with the monitor

    # Custom logic to calculate the time spent in each RRC state
    state_durations = {}
    def custom_rrc_state_callback(msg):
        state = msg.data.get('RRC State')
        timestamp = msg.timestamp
        if state and timestamp:
            if state not in state_durations:
                state_durations[state] = 0
            # Assuming the timestamp is in seconds, accumulate duration
            state_durations[state] += 1  # Increment counter for each message

        # Log state durations periodically
        if sum(state_durations.values()) % 100 == 0:  # Log every 100 messages
            for state, duration in state_durations.items():
                print(f"Duration in {state}: {duration} seconds")

    # Override existing callback with custom logic
    wcdma_rrc_analyzer.__callback_rrc_state = custom_rrc_state_callback

    # Start the monitoring
    src.run()
