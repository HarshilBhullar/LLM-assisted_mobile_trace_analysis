
#!/usr/bin/python
# Filename: modified-offline-analysis-example.py
import os
import sys

"""
Modified offline analysis by replaying logs
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, LteMeasurementAnalyzer

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

    lte_meas_analyzer = LteMeasurementAnalyzer()
    lte_meas_analyzer.set_source(src)

    # Example modification: Calculate and print average RSRP and RSRQ at the end
    def print_average_metrics():
        rsrp_list = lte_meas_analyzer.get_rsrp_list()
        rsrq_list = lte_meas_analyzer.get_rsrq_list()

        if rsrp_list:
            average_rsrp = sum(rsrp_list) / len(rsrp_list)
            print(f"Average RSRP: {average_rsrp:.2f} dBm")
        else:
            print("No RSRP measurements available.")

        if rsrq_list:
            average_rsrq = sum(rsrq_list) / len(rsrq_list)
            print(f"Average RSRQ: {average_rsrq:.2f} dB")
        else:
            print("No RSRQ measurements available.")

    # Start the monitoring
    src.run()

    # Print modified metrics
    print_average_metrics()
