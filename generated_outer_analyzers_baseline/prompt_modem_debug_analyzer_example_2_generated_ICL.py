
#!/usr/bin/python
# Filename: run_modem_debug_analyzer.py
"""
Run ModemDebugAnalyzer with an OfflineReplayer data source

Author: Yuanjie Li
"""

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger
from modem_debug_analyzer import ModemDebugAnalyzer

def main():
    # Initialize the OfflineReplayer as the data source
    src = OfflineReplayer()
    src.set_input_path("<path_to_logs_directory>")  # Replace with the actual log directory path

    # Enable specific log types
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")
    src.enable_log("5G_NR_PHY_Channel_Quality")  # Extra log type for monitoring

    # Configure MsgLogger to decode messages and save to a file
    msg_logger = MsgLogger()
    msg_logger.set_decode_format(MsgLogger.XML)
    msg_logger.save_decoded_msg_as("modified_test.txt")
    msg_logger.set_source(src)

    # Create an instance of ModemDebugAnalyzer and attach it to the data source
    analyzer = ModemDebugAnalyzer()
    analyzer.set_source(src)

    # Run the data source to start monitoring
    src.run()

if __name__ == "__main__":
    main()
