
#!/usr/bin/python
# Filename: outer_analyzer.py

import sys
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger
from lte_phy_analyzer import LtePhyAnalyzer  # Import the custom LtePhyAnalyzer

def additional_logging_callback(msg):
    """
    Callback function to log additional information for "LTE_PHY_PUCCH_Tx_Report" messages.
    
    :param msg: the message to process
    """
    log_item = msg.data.decode()
    records = log_item['Records']
    timestamp = str(log_item['timestamp'])

    for record in records:
        pucch_tx_power = record['PUCCH Tx Power (dBm)']
        print(f"Additional Logging - Timestamp: {timestamp}, PUCCH Tx Power: {pucch_tx_power} dBm")

def main(log_dir):
    # Initialize OfflineReplayer
    src = OfflineReplayer()
    src.set_input_path(log_dir)
    
    # Enable specific logs for LTE and 5G measurements
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")
    
    # Set up MsgLogger
    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as('modified_test.txt')
    logger.set_source(src)
    
    # Instantiate LtePhyAnalyzer and set its source
    lte_phy_analyzer = LtePhyAnalyzer()
    lte_phy_analyzer.set_source(src)
    
    # Register callback for additional logging
    lte_phy_analyzer.add_source_callback(additional_logging_callback, "LTE_PHY_PUCCH_Tx_Report")
    
    # Run the OfflineReplayer
    src.run()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python outer_analyzer.py <log-directory>")
        sys.exit(1)

    log_directory = sys.argv[1]
    main(log_directory)
