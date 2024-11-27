
#!/usr/bin/python
# Filename: offline-analysis-modified-example.py
import os
import sys

"""
Offline analysis by replaying logs
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
    logger.save_decoded_msg_as("./modified_test.txt")  # Changed output file name
    logger.set_source(src)

    lte_mac_analyzer = LteMacAnalyzer()
    lte_mac_analyzer.set_source(src)

    # Additional metric: Calculate average grant utilization over a period
    total_grant_received = 0
    total_grant_utilized = 0
    count = 0

    def custom_msg_callback(msg):
        if msg.type_id == "LTE_MAC_UL_Tx_Statistics":
            log_item = msg.data.decode()

            grant_received = 0
            grant_utilized = 0

            for i in range(0, len(log_item['Subpackets'])):
                grant_received += log_item['Subpackets'][i]['Sample']['Grant received']
                grant_utilized += log_item['Subpackets'][i]['Sample']['Grant utilized']

            total_grant_received += grant_received
            total_grant_utilized += grant_utilized
            count += 1

            if count > 0:
                avg_utilization = round(100.0 * total_grant_utilized / total_grant_received, 2)
                print(f"Average Grant Utilization: {avg_utilization}%")

    lte_mac_analyzer.add_source_callback(custom_msg_callback)

    # Start the monitoring
    src.run()
