
#!/usr/bin/python
# Filename: modified-offline-analysis-example.py
import os
import sys

"""
Offline analysis by replaying logs with additional metrics
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, LteMacAnalyzer

if __name__ == "__main__":

    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")
    # src.enable_log_all()

    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./test.txt")
    logger.set_source(src)

    lte_mac_analyzer = LteMacAnalyzer()
    lte_mac_analyzer.set_source(src)

    # Custom processing: Calculate average UL grant utilization
    total_grant_received = 0
    total_grant_utilized = 0

    def custom_msg_callback(msg):
        global total_grant_received, total_grant_utilized
        if msg.type_id == "MAC_UL_GRANT":
            grant_info = msg.data.decode()
            total_grant_received += int(grant_info['received'])
            total_grant_utilized += int(grant_info['used'])

    lte_mac_analyzer.add_source_callback(custom_msg_callback)

    # Start the monitoring
    src.run()

    # Calculate and print average UL grant utilization
    if total_grant_received > 0:
        average_grant_utilization = (total_grant_utilized / total_grant_received) * 100
        print("Average UL Grant Utilization: {:.2f}%".format(average_grant_utilization))
    else:
        print("No UL grants were received.")
