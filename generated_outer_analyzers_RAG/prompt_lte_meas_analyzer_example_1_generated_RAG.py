
#!/usr/bin/python
# Filename: offline-analysis-lte-measurement.py
import sys

"""
Offline analysis by replaying logs for LTE measurements
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, LteMeasurementAnalyzer

if __name__ == "__main__":

    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")
    
    # Enable specific logs for LTE and 5G
    src.enable_log("LTE_PHY_Connected_Mode_Intra_Freq_Meas")
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("LTE_PHY_Connected_Mode_Neighbor_Measurement")
    src.enable_log("LTE_PHY_Inter_RAT_Measurement")
    src.enable_log("LTE_PHY_Inter_RAT_CDMA_Measurement")

    # Configure logger
    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./lte_measurement_logs.txt")
    logger.set_source(src)

    # Integrate LteMeasurementAnalyzer
    lte_measurement_analyzer = LteMeasurementAnalyzer()
    lte_measurement_analyzer.set_source(src)

    # Start the monitoring
    src.run()

    # Calculate average RSRP and RSRQ
    rsrp_list = lte_measurement_analyzer.get_rsrp_list()
    rsrq_list = lte_measurement_analyzer.get_rsrq_list()

    avg_rsrp = sum(rsrp_list) / len(rsrp_list) if rsrp_list else 0
    avg_rsrq = sum(rsrq_list) / len(rsrq_list) if rsrq_list else 0

    print(f"Average RSRP: {avg_rsrp:.2f} dBm")
    print(f"Average RSRQ: {avg_rsrq:.2f} dB")
