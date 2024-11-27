
#!/usr/bin/python
# Filename: outer_lte_mac_analyzer.py

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger
from lte_mac_analyzer import LteMacAnalyzer

def main():
    # Initialize the Offline Replayer
    src = OfflineReplayer()
    src.set_input_path("./logs/")

    # Enable specific logs required for the analysis
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")
    src.enable_log("LTE_MAC_UL_Tx_Statistics")

    # Set up the LTE MAC Analyzer
    analyzer = LteMacAnalyzer()
    analyzer.set_source(src)

    # Optionally, set up a message logger to log decoded messages
    logger = MsgLogger()
    logger.set_source(src)
    logger.set_decode_format(MsgLogger.JSON)
    logger.save_decoded_msg("./test_modified.txt")

    # Start the analysis
    src.run()

if __name__ == "__main__":
    main()
