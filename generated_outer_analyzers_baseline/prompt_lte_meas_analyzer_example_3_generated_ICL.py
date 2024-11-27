
#!/usr/bin/python
# Filename: lte_measurement_outer_analyzer.py

"""
Outer analyzer script for LTE radio measurements

Author: Your Name
"""

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger
from lte_measurement_analyzer import LteMeasurementAnalyzer
import numpy as np
import os

def calculate_and_log_average(analyzer):
    """
    Calculate and log the average RSRP and RSRQ measurements.

    :param analyzer: An instance of LteMeasurementAnalyzer
    """
    rsrp_list = analyzer.get_rsrp_list()
    rsrq_list = analyzer.get_rsrq_list()

    if rsrp_list:
        avg_rsrp = np.mean(rsrp_list)
    else:
        avg_rsrp = None

    if rsrq_list:
        avg_rsrq = np.mean(rsrq_list)
    else:
        avg_rsrq = None

    log_message = f"Average RSRP: {avg_rsrp} dBm, Average RSRQ: {avg_rsrq} dB"
    print(log_message)

    with open("measurement_results.txt", "a") as log_file:
        log_file.write(log_message + "\n")

if __name__ == "__main__":
    # Initialize OfflineReplayer
    src = OfflineReplayer()
    src.set_input_path("path/to/log/files")

    # Enable specific logs for LTE events
    src.enable_log("LTE_PHY_Connected_Mode_Intra_Freq_Meas")
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("LTE_PHY_Connected_Mode_Neighbor_Measurement")
    src.enable_log("LTE_PHY_Inter_RAT_Measurement")
    src.enable_log("LTE_PHY_Inter_RAT_CDMA_Measurement")

    # Initialize MsgLogger
    msg_logger = MsgLogger()
    msg_logger.set_source(src)
    msg_logger.set_decode_format(MsgLogger.XML)

    # Initialize LteMeasurementAnalyzer
    lte_analyzer = LteMeasurementAnalyzer()
    lte_analyzer.set_source(src)

    # Start the monitoring
    src.run()

    # Calculate and log average measurements
    calculate_and_log_average(lte_analyzer)
