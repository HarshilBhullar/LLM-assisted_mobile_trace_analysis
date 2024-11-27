
#!/usr/bin/python
# Filename: modified-lte-dl-retx-analysis.py

import os
import sys

"""
Modified analysis to monitor downlink MAC and RLC retransmission delay.
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, LteDlRetxAnalyzer

if __name__ == "__main__":

    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")
    # src.enable_log_all()

    src.enable_log("LTE_RLC_UL_AM_All_PDU")
    src.enable_log("LTE_RLC_DL_AM_All_PDU")

    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./decoded_messages.txt")  # Output file for verification
    logger.set_source(src)

    lte_dl_retx_analyzer = LteDlRetxAnalyzer()
    lte_dl_retx_analyzer.set_source(src)

    def calculate_enhanced_metric():
        for rb_id, bearer in lte_dl_retx_analyzer.bearer_entity.items():
            total_mac_retx = len(bearer.mac_retx)
            total_rlc_retx = len(bearer.rlc_retx)
            print(f"Radio Bearer ID {rb_id}: Total MAC Retransmissions = {total_mac_retx}, Total RLC Retransmissions = {total_rlc_retx}")

    # Start the monitoring
    src.run()

    # Calculate enhanced retransmission metrics after log replay
    calculate_enhanced_metric()
