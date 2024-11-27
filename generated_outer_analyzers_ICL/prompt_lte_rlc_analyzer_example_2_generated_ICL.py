
#!/usr/bin/python
# Filename: outer_lte_rlc_analysis.py

import sys
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, LteRlcAnalyzer

if __name__ == "__main__":
    try:
        # Initialize an OfflineReplayer
        src = OfflineReplayer()
        src.set_input_path("./logs/")

        # Enable specific logs for analysis
        src.enable_log("LTE_PHY_Serv_Cell_Measurement")
        src.enable_log("5G_NR_RRC_OTA_Packet")
        src.enable_log("LTE_RRC_OTA_Packet")
        src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

        # Set up message logger
        logger = MsgLogger()
        logger.set_decode_format(MsgLogger.XML)
        logger.set_dump_type(MsgLogger.FILE_ONLY)
        logger.save_decoded_msg_as("./modified_test.txt")
        logger.set_source(src)

        # Integrate the LteRlcAnalyzer
        lte_rlc_analyzer = LteRlcAnalyzer()
        lte_rlc_analyzer.set_source(src)

        # Start the monitoring
        print("Starting the analysis...")
        src.run()
        print("Analysis completed successfully.")

    except Exception as e:
        print(f"An error occurred during the analysis: {e}")
