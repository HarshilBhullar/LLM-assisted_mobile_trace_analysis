
#!/usr/bin/python

import sys

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger
from nr_rrc_analyzer import NrRrcAnalyzer

def packet_count_callback(msg):
    global packet_count
    packet_count += 1
    print(f"Packet {packet_count} processed.")

if __name__ == "__main__":

    # Initialize the packet counter
    packet_count = 0

    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")
    
    # Enable specific logs
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    # Initialize and configure logger
    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./nr_rrc_decoded.txt")
    logger.set_source(src)

    # Initialize the NR RRC Analyzer
    nr_rrc_analyzer = NrRrcAnalyzer()
    nr_rrc_analyzer.set_source(src)
    
    # Set a callback to track processed packets
    src.add_source_callback(packet_count_callback)

    # Start the monitoring
    src.run()
