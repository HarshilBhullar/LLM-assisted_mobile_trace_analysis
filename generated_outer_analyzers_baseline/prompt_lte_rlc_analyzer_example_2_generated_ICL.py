
#!/usr/bin/python
# Filename: outer_analyzer.py

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.analyzer import MsgLogger
from lte_rlc_analyzer import LteRlcAnalyzer

def main():
    try:
        # Initialize OfflineReplayer
        src = OfflineReplayer()
        src.set_input_path("./logs/")
        
        # Enable specific log types for analysis
        src.enable_log("LTE_PHY_Serv_Cell_Measurement")
        src.enable_log("5G_NR_RRC_OTA_Packet")
        src.enable_log("LTE_RRC_OTA_Packet")
        src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

        # Setup message logger
        logger = MsgLogger()
        logger.set_decode_format(MsgLogger.XML)
        logger.save_decoded_msg_as("./modified_test.txt")
        logger.set_source(src)

        # Integrate the custom LteRlcAnalyzer
        analyzer = LteRlcAnalyzer()
        analyzer.set_source(src)

        # Execute the log replay
        print("Starting log replay and analysis...")
        src.run()
        print("Log replay and analysis completed successfully.")

    except Exception as e:
        print(f"An error occurred during execution: {e}")

if __name__ == "__main__":
    main()
