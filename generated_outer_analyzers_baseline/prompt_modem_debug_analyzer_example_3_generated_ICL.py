
#!/usr/bin/python
# Filename: outer_modem_debug_analyzer.py

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger
from modem_debug_analyzer import ModemDebugAnalyzer

def main():
    # Initialize the OfflineReplayer
    src = OfflineReplayer()
    src.set_input_path("./logs/")

    # Enable specific cellular event logs
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    # Set up a message logger
    logger = MsgLogger()
    logger.set_source(src)
    logger.set_decode_format(MsgLogger.XML)
    logger.save_decoded_msg_as("modified_test.txt")

    # Integrate the custom ModemDebugAnalyzer
    modem_debug_analyzer = ModemDebugAnalyzer()
    modem_debug_analyzer.set_source(src)

    # Enable additional log
    src.enable_log("LTE_PHY_PDSCH_Stat_Indication")

    # Start the log replay process
    src.run()

if __name__ == "__main__":
    main()
