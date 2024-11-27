
#!/usr/bin/python
# Filename: lte_measurement_analysis.py

import os
import sys

"""
LTE radio measurements using LteMeasurementAnalyzer
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, LteMeasurementAnalyzer

def calculate_and_log_average(analyzer):
    rsrp_list = analyzer.get_rsrp_list()
    rsrq_list = analyzer.get_rsrq_list()
    
    avg_rsrp = sum(rsrp_list) / len(rsrp_list) if rsrp_list else 0
    avg_rsrq = sum(rsrq_list) / len(rsrq_list) if rsrq_list else 0
    
    log_message = f"Average RSRP: {avg_rsrp:.2f} dBm, Average RSRQ: {avg_rsrq:.2f} dB"
    print(log_message)
    
    with open("lte_measurement_averages.txt", "w") as log_file:
        log_file.write(log_message + "\n")

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
    logger.save_decoded_msg_as("./lte_measurement_log.xml")
    logger.set_source(src)

    lte_measurement_analyzer = LteMeasurementAnalyzer()
    lte_measurement_analyzer.set_source(src)

    # Start the monitoring
    src.run()

    # After running, calculate and log the average RSRP and RSRQ
    calculate_and_log_average(lte_measurement_analyzer)
