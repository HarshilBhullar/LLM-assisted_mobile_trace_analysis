
#!/usr/bin/python
# Filename: modified-offline-analysis-example.py
import os
import sys

"""
Offline analysis by replaying logs with additional metrics
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, MmAnalyzer

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

    mm_analyzer = MmAnalyzer()
    mm_analyzer.set_source(src)

    # Additional analysis: Calculate total service spans for LTE and UMTS
    def calculate_total_span(spans):
        total_duration = 0
        for span in spans:
            if span.end and span.start:
                total_duration += (span.end - span.start).total_seconds()
        return total_duration

    # Start the monitoring
    src.run()

    # Calculate and print additional metrics
    lte_service_duration = calculate_total_span(mm_analyzer.get_lte_normal_service_log())
    umts_service_duration = calculate_total_span(mm_analyzer.get_umts_normal_service_log())

    print("Total LTE Normal Service Duration: {:.2f} seconds".format(lte_service_duration))
    print("Total UMTS Normal Service Duration: {:.2f} seconds".format(umts_service_duration))
