
#!/usr/bin/python
# Filename: modified-offline-analysis-example.py
import os
import sys

"""
Modified offline analysis by replaying logs
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
    logger.save_decoded_msg_as("./modified_test.txt")
    logger.set_source(src)

    mm_analyzer = MmAnalyzer()
    mm_analyzer.set_source(src)

    # New logic to calculate and print additional metrics
    def print_additional_metrics(analyzer):
        umts_service_duration = sum(
            (span.end - span.start).total_seconds() for span in analyzer.get_umts_normal_service_log() if span.end)
        lte_service_duration = sum(
            (span.end - span.start).total_seconds() for span in analyzer.get_lte_normal_service_log() if span.end)

        print(f"UMTS Normal Service Duration: {umts_service_duration} seconds")
        print(f"LTE Normal Service Duration: {lte_service_duration} seconds")
    
    # Start the monitoring
    src.run()

    # Print additional metrics after monitoring
    print_additional_metrics(mm_analyzer)
