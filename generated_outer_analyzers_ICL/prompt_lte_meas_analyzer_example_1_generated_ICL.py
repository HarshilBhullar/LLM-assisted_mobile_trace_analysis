
#!/usr/bin/python
# Filename: lte_measurement_analysis.py
import os
import sys

"""
LTE measurement analysis by replaying logs
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, LteMeasurementAnalyzer

if __name__ == "__main__":

    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")

    src.enable_log("LTE_PHY_Connected_Mode_Intra_Freq_Meas")
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("LTE_PHY_Connected_Mode_Neighbor_Measurement")
    src.enable_log("LTE_PHY_Inter_RAT_Measurement")
    src.enable_log("LTE_PHY_Inter_RAT_CDMA_Measurement")

    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./lte_measurement_output.txt")
    logger.set_source(src)

    lte_measurement_analyzer = LteMeasurementAnalyzer()
    lte_measurement_analyzer.set_source(src)

    # Start the monitoring
    src.run()

    # Calculate and print average RSRP and RSRQ
    rsrp_list = lte_measurement_analyzer.get_rsrp_list()
    rsrq_list = lte_measurement_analyzer.get_rsrq_list()

    if rsrp_list:
        avg_rsrp = sum(rsrp_list) / len(rsrp_list)
        print(f"Average RSRP: {avg_rsrp} dBm")
    else:
        print("No RSRP measurements available.")

    if rsrq_list:
        avg_rsrq = sum(rsrq_list) / len(rsrq_list)
        print(f"Average RSRQ: {avg_rsrq} dB")
    else:
        print("No RSRQ measurements available.")
