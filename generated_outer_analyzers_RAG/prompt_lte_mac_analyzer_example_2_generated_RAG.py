
#!/usr/bin/python
# Filename: modified-offline-analysis-with-metrics.py

import sys

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, LteMacAnalyzer

def custom_metric_processing(lte_mac_analyzer):
    """
    Perform additional metric calculations or data processing.
    """
    # Example calculation: Average UL Queue Length
    if lte_mac_analyzer.queue_length > 0:
        print("Final UL Queue Length:", lte_mac_analyzer.queue_length)

if __name__ == "__main__":
    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")

    # Enable necessary logs
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    # Setup logger to save decoded messages
    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./decoded_messages.xml")
    logger.set_source(src)

    # Instantiate and configure LteMacAnalyzer
    lte_mac_analyzer = LteMacAnalyzer()
    lte_mac_analyzer.set_source(src)

    # Start the monitoring process
    src.run()

    # Perform custom metric processing after analysis
    custom_metric_processing(lte_mac_analyzer)
