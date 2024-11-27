
#!/usr/bin/python
# Filename: offline-analysis-enhanced-metrics.py
import os
import sys

"""
Offline analysis by replaying logs with additional metrics
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, LteDlRetxAnalyzer

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
    logger.save_decoded_msg_as("./test.txt")
    logger.set_source(src)

    lte_dl_retx_analyzer = LteDlRetxAnalyzer()
    lte_dl_retx_analyzer.set_source(src)

    # Additional processing: Calculate average RLC retransmission delay
    def calculate_average_rlc_retx_delay():
        total_rlc_retx_delay = 0
        rlc_retx_count = 0
        for bearer_id, bearer_entity in lte_dl_retx_analyzer.bearer_entity.items():
            for entry in bearer_entity.rlc_retx:
                total_rlc_retx_delay += entry['rlc_retx']
                rlc_retx_count += 1
        average_rlc_retx_delay = (total_rlc_retx_delay / rlc_retx_count) if rlc_retx_count > 0 else 0
        return average_rlc_retx_delay

    # Start the monitoring
    src.run()

    # Perform the average RLC retransmission delay calculation after monitoring
    average_rlc_retx_delay = calculate_average_rlc_retx_delay()
    print(f"Average RLC Retransmission Delay: {average_rlc_retx_delay} ms")
