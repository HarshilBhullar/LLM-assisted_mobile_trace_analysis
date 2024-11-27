
#!/usr/bin/python
# Filename: offline-analysis-lte-mac.py

"""
Offline analysis for LTE MAC-layer metrics
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, LteMacAnalyzer

class CustomLteMacAnalyzer(LteMacAnalyzer):
    def __init__(self):
        super().__init__()
        self.total_grant_received = 0
        self.total_grant_utilized = 0

    def __msg_callback(self, msg):
        super().__msg_callback(msg)
        
        if msg.type_id == "LTE_MAC_UL_Tx_Statistics":
            log_item = msg.data.decode()
            for i in range(0, len(log_item['Subpackets'])):
                self.total_grant_received += log_item['Subpackets'][i]['Sample']['Grant received']
                self.total_grant_utilized += log_item['Subpackets'][i]['Sample']['Grant utilized']

    def calculate_average_ul_grant_utilization(self):
        if self.total_grant_received > 0:
            average_utilization = (self.total_grant_utilized / self.total_grant_received) * 100
            print("Average UL Grant Utilization: {:.2f}%".format(average_utilization))
        else:
            print("No UL Grants were received.")

if __name__ == "__main__":

    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")
    # src.enable_log_all()

    src.enable_log("LTE_MAC_UL_Tx_Statistics")
    src.enable_log("LTE_MAC_UL_Buffer_Status_Internal")
    src.enable_log("LTE_PHY_PDSCH_Stat_Indication")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")

    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./lte_mac_analysis.txt")
    logger.set_source(src)

    lte_mac_analyzer = CustomLteMacAnalyzer()
    lte_mac_analyzer.set_source(src)

    # Start the monitoring
    src.run()

    # Calculate and print the average UL grant utilization
    lte_mac_analyzer.calculate_average_ul_grant_utilization()
