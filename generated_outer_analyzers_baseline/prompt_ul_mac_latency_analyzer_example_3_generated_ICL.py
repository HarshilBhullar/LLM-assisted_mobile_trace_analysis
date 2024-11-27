
#!/usr/bin/python
# Filename: ul_mac_latency_outer_analyzer.py

from mobile_insight.analyzer import MsgLogger
from mobile_insight.monitor import OfflineReplayer
from ul_mac_latency_analyzer import UlMacLatencyAnalyzer

class UlMacLatencyOuterAnalyzer:
    def __init__(self, log_path, output_file):
        self.log_path = log_path
        self.output_file = output_file

    def setup_replayer(self):
        # Initialize the offline replayer
        self.src = OfflineReplayer()
        self.src.set_input_path(self.log_path)

        # Enable specific logs
        self.src.enable_log("LTE_PHY_Serv_Cell_Measurement")
        self.src.enable_log("5G_NR_RRC_OTA_Packet")
        self.src.enable_log("LTE_RRC_OTA_Packet")
        self.src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    def setup_logger(self):
        # Initialize and configure the message logger
        self.logger = MsgLogger()
        self.logger.set_decode_format(MsgLogger.XML)
        self.logger.save_decoded_msg_as(self.output_file)
        self.logger.set_source(self.src)

    def setup_analyzer(self):
        # Initialize and link the inner analyzer
        self.analyzer = UlMacLatencyAnalyzer()
        self.analyzer.set_source(self.src)

        # Add custom callback for additional analysis
        self.analyzer.add_analyzer_callback("LTE_MAC_UL_Buffer_Status_Internal", self.custom_callback)

    def custom_callback(self, msg):
        # Custom callback to calculate and print average buffer length over time
        if msg.type_id == "LTE_MAC_UL_Buffer_Status_Internal":
            log_item = msg.data.decode()
            if 'Subpackets' in log_item:
                total_buffer_length = 0
                sample_count = 0
                for subpacket in log_item['Subpackets']:
                    if 'Samples' in subpacket:
                        for sample in subpacket['Samples']:
                            for lcid in sample['LCIDs']:
                                if 'New bytes' in lcid:
                                    total_buffer_length += int(lcid['New bytes'])
                                    sample_count += 1
                if sample_count > 0:
                    avg_buffer_length = total_buffer_length / sample_count
                    print(f"Average Buffer Length: {avg_buffer_length}")

    def run(self):
        # Execute the offline replayer to process logs
        self.setup_replayer()
        self.setup_logger()
        self.setup_analyzer()
        self.src.run()

if __name__ == "__main__":
    log_path = "path/to/log/files"  # Replace with actual path to log files
    output_file = "modified_test.txt"

    analyzer = UlMacLatencyOuterAnalyzer(log_path, output_file)
    analyzer.run()
