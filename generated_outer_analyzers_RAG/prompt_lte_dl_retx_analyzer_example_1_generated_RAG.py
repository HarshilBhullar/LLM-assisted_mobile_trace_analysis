
#!/usr/bin/python
# Filename: offline_analysis_with_custom_analyzer.py

import os
import sys

"""
Offline analysis by replaying logs and calculating additional metrics.
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger
from lte_dl_retx_analyzer import LteDlRetxAnalyzer

def calculate_average_rlc_retx_delay(analyzer):
    rlc_delay = 0.0
    rlc_delay_sample = 0

    for _, bearer in analyzer.bearer_entity.items():
        for item in bearer.rlc_retx:
            rlc_delay += item['rlc_retx']
            rlc_delay_sample += 1

    avg_rlc_delay = float(rlc_delay) / rlc_delay_sample if rlc_delay_sample > 0 else 0.0
    return avg_rlc_delay

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
    logger.save_decoded_msg_as("./test.txt")
    logger.set_source(src)

    lte_dl_retx_analyzer = LteDlRetxAnalyzer()
    lte_dl_retx_analyzer.set_source(src)

    # Start the monitoring
    src.run()

    # Calculate and print the average RLC retransmission delay
    avg_rlc_retx_delay = calculate_average_rlc_retx_delay(lte_dl_retx_analyzer)
    print(f"Average RLC Retransmission Delay: {avg_rlc_retx_delay}")
