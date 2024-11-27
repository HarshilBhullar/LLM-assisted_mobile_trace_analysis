
#!/usr/bin/python
# Filename: outer_analyzer.py

from mobile_insight.analyzer.offline_replayer import OfflineReplayer
from mobile_insight.analyzer.msg_logger import MsgLogger
from wcdma_rrc_analyzer import WcdmaRrcAnalyzer

class OuterAnalyzer:
    def __init__(self):
        # Setup OfflineReplayer
        self.replayer = OfflineReplayer()
        self.replayer.set_input_path("./logs/")
        
        # Enable relevant logs
        self.replayer.enable_log("LTE_PHY_Serv_Cell_Measurement")
        self.replayer.enable_log("5G_NR_RRC_OTA_Packet")
        self.replayer.enable_log("LTE_RRC_OTA_Packet")
        self.replayer.enable_log("LTE_NB1_ML1_GM_DCI_Info")
        
        # Setup MsgLogger
        self.logger = MsgLogger()
        self.logger.set_decode_format(MsgLogger.XML)
        self.logger.save_decoded_msg_as("modified_test.txt")
        self.logger.set_print_in_console(False)
        self.logger.set_source(self.replayer)
        
        # Setup WcdmaRrcAnalyzer
        self.rrc_analyzer = WcdmaRrcAnalyzer()
        self.rrc_analyzer.set_source(self.replayer)

        # Initialize custom RRC state analysis
        self.rrc_state_durations = {}
        self.message_count = 0

    def custom_rrc_state_callback(self, msg):
        current_state = msg.data['RRC State']
        timestamp = msg.data['Timestamp']

        # Initialize state durations if not present
        if current_state not in self.rrc_state_durations:
            self.rrc_state_durations[current_state] = 0

        # Increment state duration
        self.rrc_state_durations[current_state] += 1
        self.message_count += 1

        # Print cumulative duration every 100 messages
        if self.message_count % 100 == 0:
            print("Cumulative RRC State Durations:")
            for state, duration in self.rrc_state_durations.items():
                print(f"{state}: {duration} messages")

    def run(self):
        # Override default RRC state callback
        self.rrc_analyzer.__callback_rrc_state = self.custom_rrc_state_callback
        
        # Start replaying logs
        self.replayer.run()

if __name__ == "__main__":
    analyzer = OuterAnalyzer()
    analyzer.run()
