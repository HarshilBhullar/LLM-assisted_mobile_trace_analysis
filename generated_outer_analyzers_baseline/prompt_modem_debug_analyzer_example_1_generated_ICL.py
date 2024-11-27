
#!/usr/bin/python
# Filename: outer_modem_debug_analyzer.py
"""
Outer analyzer for ModemDebugAnalyzer

Author: Yuanjie Li
"""

from mobile_insight.monitor.offline_replayer import OfflineReplayer
from mobile_insight.analyzer.analyzer import MsgLogger
from modem_debug_analyzer import ModemDebugAnalyzer

# Initialize the monitor
src = OfflineReplayer()
src.set_input_path("./logs")  # Set the path to the logs directory

# Enable logging for additional message types
src.enable_log("LTE_PHY_Serv_Cell_Measurement")
src.enable_log("5G_NR_RRC_OTA_Packet")
src.enable_log("LTE_RRC_OTA_Packet")
src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

# Use MsgLogger to log messages in XML format
xml_logger = MsgLogger()
xml_logger.set_decode_format(MsgLogger.XML)
xml_logger.save_decoded_msg_as("test_modified.txt")
xml_logger.set_source(src)

# Create an instance of ModemDebugAnalyzer
modem_analyzer = ModemDebugAnalyzer()
modem_analyzer.set_source(src)

# Custom callback function to calculate the total number of "Modem_debug_message" messages
class ModemDebugAnalyzerWithCount(ModemDebugAnalyzer):
    def __init__(self):
        super().__init__()
        self.modem_debug_count = 0

    def __msg_callback(self, msg):
        super().__msg_callback(msg)
        if msg.type_id == "Modem_debug_message":
            self.modem_debug_count += 1

# Create an instance of the modified analyzer with count functionality
modem_analyzer_with_count = ModemDebugAnalyzerWithCount()
modem_analyzer_with_count.set_source(src)

# Execute the monitoring
src.run()

# Print the total number of "Modem_debug_message" messages processed
print(f"Total 'Modem_debug_message' messages processed: {modem_analyzer_with_count.modem_debug_count}")
