
#!/usr/bin/python
# Filename: run_lte_rlc_analysis.py

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger
from lte_rlc_analyzer import LteRlcAnalyzer

def main():
    # Setup and Initialization
    src = OfflineReplayer()
    src.set_input_path("./logs/")

    # Enable specific logs
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    # Logging Configuration
    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.save_decoded_msg_as("./modified_test.txt")
    logger.set_source(src)

    # Analyzer Integration
    analyzer = LteRlcAnalyzer()
    analyzer.set_source(src)

    # Modified Metrics or Calculations
    print("Starting modified offline analysis...")

    # Execution of Analysis
    src.run()

if __name__ == "__main__":
    main()
