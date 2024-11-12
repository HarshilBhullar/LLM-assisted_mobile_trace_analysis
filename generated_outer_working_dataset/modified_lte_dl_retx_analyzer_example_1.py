
#!/usr/bin/python
# Filename: modified-offline-analysis-example.py
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

    # Additional processing: Calculate the average RLC retransmission delay
    def calculate_average_rlc_retx_delay(analyzer):
        total_delay = 0
        count = 0
        for bearer in analyzer.bearer_entity.values():
            for entry in bearer.rlc_retx:
                total_delay += entry['rlc_retx']
                count += 1
        return total_delay / count if count > 0 else 0

    # Start the monitoring
    src.run()

    # Output the additional metric
    avg_rlc_retx_delay = calculate_average_rlc_retx_delay(lte_dl_retx_analyzer)
    print(f"Average RLC Retransmission Delay: {avg_rlc_retx_delay} ms")
