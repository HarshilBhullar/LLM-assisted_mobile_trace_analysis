
#!/usr/bin/python
# Filename: outer_lte_dl_retx_analyzer.py

import sys

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, LteDlRetxAnalyzer

def calculate_retx_statistics(lteAnalyzer):
    mac_retx_count = 0
    rlc_retx_count = 0

    for _, bearer in lteAnalyzer.bearer_entity.items():
        mac_retx_count += len(bearer.mac_retx)
        rlc_retx_count += len(bearer.rlc_retx)

    print(f"Total MAC Retransmissions: {mac_retx_count}")
    print(f"Total RLC Retransmissions: {rlc_retx_count}")

if __name__ == "__main__":
    # Initialize the data source
    src = OfflineReplayer()
    src.set_input_path('./logs/offline_log_examples/20201115_181637_Xiaomi-Mi10_46000.mi2log')

    # Enable specific signaling messages
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    # Initialize and configure the logger
    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./lte_dl_retx_analysis.txt")
    logger.set_source(src)

    # Initialize and configure the analyzer
    lteAnalyzer = LteDlRetxAnalyzer()
    lteAnalyzer.set_source(src)

    # Start the monitoring and processing
    src.run()

    # Calculate and output retransmission statistics
    calculate_retx_statistics(lteAnalyzer)
