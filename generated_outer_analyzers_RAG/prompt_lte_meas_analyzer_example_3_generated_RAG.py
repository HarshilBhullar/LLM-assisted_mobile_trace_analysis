
#!/usr/bin/python
# Filename: lte-measurement-analyzer-example.py

import os
import sys

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.lte_measurement_analyzer import LteMeasurementAnalyzer
from mobile_insight.analyzer import MsgLogger

def calculate_and_log_average(analyzer):
    rsrp_list = analyzer.get_rsrp_list()
    rsrq_list = analyzer.get_rsrq_list()

    avg_rsrp = sum(rsrp_list) / len(rsrp_list) if rsrp_list else 0
    avg_rsrq = sum(rsrq_list) / len(rsrq_list) if rsrq_list else 0

    with open('./lte_measurement_averages.txt', 'w') as f:
        f.write("Average RSRP: {:.2f} dBm\n".format(avg_rsrp))
        f.write("Average RSRQ: {:.2f} dB\n".format(avg_rsrq))

    print("Average RSRP: {:.2f} dBm".format(avg_rsrp))
    print("Average RSRQ: {:.2f} dB".format(avg_rsrq))

if __name__ == '__main__':
    # Initialize the OfflineReplayer
    src = OfflineReplayer()
    src.set_input_path('./logs')  # Set the path to your log files

    # Enable specific logs for LTE and 5G events
    src.enable_log("LTE_PHY_Connected_Mode_Intra_Freq_Meas")
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("LTE_PHY_Connected_Mode_Neighbor_Measurement")
    src.enable_log("LTE_PHY_Inter_RAT_Measurement")
    src.enable_log("LTE_PHY_Inter_RAT_CDMA_Measurement")

    # Instantiate a MsgLogger
    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_source(src)

    # Instantiate the LteMeasurementAnalyzer
    meas_analyzer = LteMeasurementAnalyzer()
    meas_analyzer.set_source(src)

    # Run the monitoring process
    src.run()

    # Calculate and log averages
    calculate_and_log_average(meas_analyzer)
