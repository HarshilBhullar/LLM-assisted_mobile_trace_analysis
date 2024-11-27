
#!/usr/bin/python
# Filename: modified-offline-analysis-example.py
import os
import sys

"""
Modified offline analysis by replaying logs with additional metrics.
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger
from wcdma_rrc_analyzer import WcdmaRrcAnalyzer

class ExtendedWcdmaRrcAnalyzer(WcdmaRrcAnalyzer):
    def __init__(self):
        super().__init__()
        self.rrc_state_counts = {
            'CELL_FACH': 0,
            'CELL_DCH': 0,
            'URA_PCH': 0,
            'CELL_PCH': 0,
            'IDLE': 0
        }

    def __rrc_filter(self, msg):
        super().__rrc_filter(msg)
        if msg.type_id == "WCDMA_RRC_States":
            rrc_state = msg.data['RRC State']
            if rrc_state in self.rrc_state_counts:
                self.rrc_state_counts[rrc_state] += 1

    def print_state_counts(self):
        print("RRC State Counts:")
        for state, count in self.rrc_state_counts.items():
            print(f"{state}: {count}")

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

    # Analyzers
    wcdma_rrc_analyzer = ExtendedWcdmaRrcAnalyzer()
    wcdma_rrc_analyzer.set_source(src)  # bind with the monitor

    # Start the monitoring
    src.run()

    # Print RRC state counts
    wcdma_rrc_analyzer.print_state_counts()
