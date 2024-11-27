
#!/usr/bin/python
# Filename: outer_analyzer.py

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.analyzer import MsgLogger
from lte_phy_analyzer import LtePhyAnalyzer

# Initialize the Offline Replayer
src = OfflineReplayer()
src.set_input_path("./logs/")  # Set the path to the directory containing the log files

# Enable the necessary logs for analysis
src.enable_log("LTE_PHY_Serv_Cell_Measurement")
src.enable_log("5G_NR_RRC_OTA_Packet")
src.enable_log("LTE_PHY_PDSCH_Packet")
src.enable_log("LTE_PHY_PUSCH_CSF")
src.enable_log("LTE_MAC_UL_Tx_Statistics")
src.enable_log("LTE_PHY_PUCCH_Tx_Report")
src.enable_log("LTE_PHY_PUSCH_Tx_Report")

# Initialize the LtePhyAnalyzer
analyzer = LtePhyAnalyzer()
analyzer.set_source(src)

# Initialize the message logger to save logs in XML format
logger = MsgLogger()
logger.set_source(src)
logger.set_decode_format(MsgLogger.XML)
logger.save_decoded_msg_as("./output/log.xml")  # Set the path for the output XML file

# Run the offline replayer
src.run()

# After running the analysis, calculate additional metrics
# Assume that the total downlink bandwidth and timestamps are collected during the log replay
# Example: avg_downlink_bandwidth = total_downlink_bandwidth / total_duration
# Here, placeholders are used, replace with actual calculation logic based on the collected data

total_downlink_bandwidth = 0  # Placeholder, replace with actual total downlink bandwidth
total_duration = 1  # Placeholder, replace with actual duration in seconds

if total_duration > 0:
    avg_downlink_bandwidth = total_downlink_bandwidth / total_duration
    print(f"Average Downlink Bandwidth: {avg_downlink_bandwidth} Mbps")
else:
    print("Duration is zero, cannot calculate average bandwidth.")
