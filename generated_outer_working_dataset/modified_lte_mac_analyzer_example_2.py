
#!/usr/bin/python
# Filename: offline-analysis-example-modified.py
import os
import sys

"""
Offline analysis by replaying logs with additional metrics
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, LteMacAnalyzer

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

    lte_mac_analyzer = LteMacAnalyzer()
    lte_mac_analyzer.set_source(src)

    # Custom additional processing
    def custom_metric_processing():
        print("Performing additional metric calculations...")
        # Here you could add additional data processing or calculations
        # For example, you could calculate average grant utilization over a period
        # or any other custom logic needed for your analysis.

    # Start the monitoring
    src.run()

    # Perform custom metric processing after the run
    custom_metric_processing()
