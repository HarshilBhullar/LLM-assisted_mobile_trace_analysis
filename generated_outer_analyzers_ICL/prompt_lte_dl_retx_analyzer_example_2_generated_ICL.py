
#!/usr/bin/python
# Filename: lte_dl_retx_analysis_script.py

"""
Outer Analyzer to monitor downlink MAC retransmission delay and RLC retransmission delay
"""

import os
import sys

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, LteDlRetxAnalyzer

def calculate_retx_statistics(analyzer):
    mac_retx_count = 0
    rlc_retx_count = 0
    
    for bearer in analyzer.bearer_entity.values():
        mac_retx_count += len(bearer.mac_retx)
        rlc_retx_count += len(bearer.rlc_retx)
    
    print(f"Total MAC Retransmissions: {mac_retx_count}")
    print(f"Total RLC Retransmissions: {rlc_retx_count}")

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
    logger.save_decoded_msg_as("./lte_retx_analysis_log.txt")
    logger.set_source(src)

    lte_dl_retx_analyzer = LteDlRetxAnalyzer()
    lte_dl_retx_analyzer.set_source(src)

    # Start the monitoring
    src.run()

    # After processing logs, calculate retransmission statistics
    calculate_retx_statistics(lte_dl_retx_analyzer)
