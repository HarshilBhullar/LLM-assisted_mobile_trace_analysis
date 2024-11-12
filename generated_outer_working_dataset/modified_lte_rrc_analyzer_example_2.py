
#!/usr/bin/python
# Filename: modified-offline-analysis-example.py
import os
import sys

"""
Modified offline analysis by replaying logs
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, LteRrcAnalyzer

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
    logger.save_decoded_msg_as("./modified_test.txt")
    logger.set_source(src)

    lte_rrc_analyzer = LteRrcAnalyzer()
    lte_rrc_analyzer.set_source(src)  # bind with the monitor

    # New: Calculate and log average RSRP from the measurements
    def calculate_average_rsrp():
        rsrp_values = []
        def callback(event):
            if event.type_id == 'MEAS_PCELL':
                rsrp_values.append(event.data['rsrp'])
                avg_rsrp = sum(rsrp_values) / len(rsrp_values)
                print(f"Average RSRP: {avg_rsrp:.2f} dBm")
                
        lte_rrc_analyzer.add_callback(callback)

    calculate_average_rsrp()

    # Start the monitoring
    src.run()
