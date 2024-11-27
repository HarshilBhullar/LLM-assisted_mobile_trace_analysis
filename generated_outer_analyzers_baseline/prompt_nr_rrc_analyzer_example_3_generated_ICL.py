
#!/usr/bin/python
# Filename: outer_nr_rrc_analyzer.py

import os
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger
from nr_rrc_analyzer import NrRrcAnalyzer

def main():
    # Set the input path for log files
    input_path = "./path_to_log_files"
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input path {input_path} does not exist.")

    # Initialize the offline replayer as the data source
    src = OfflineReplayer()
    src.set_input_path(input_path)

    # Enable specific log types
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    # Instantiate the MsgLogger to log and save decoded messages
    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.save_decoded_msg_as("decoded_messages.xml")
    logger.set_source(src)

    # Instantiate the NrRrcAnalyzer and bind it to the data source
    nr_rrc_analyzer = NrRrcAnalyzer()
    nr_rrc_analyzer.set_source(src)

    # Initialize packet count
    packet_count = [0]

    # Define a custom callback function to log the number of packets processed
    def log_packet_count(msg):
        packet_count[0] += 1
        print(f"Packet count: {packet_count[0]}")

    # Attach the callback function to the NrRrcAnalyzer
    nr_rrc_analyzer.add_callback(log_packet_count)

    # Run the analysis
    src.run()

if __name__ == "__main__":
    main()
