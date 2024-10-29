
#!/usr/bin/python
# Filename: modified-offline-analysis-example.py
import os
import sys

"""
Modified offline analysis by replaying logs
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, NrRrcAnalyzer, LteRrcAnalyzer, LteMeasurementAnalyzer

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
    logger.set_decode_format(MsgLogger.JSON)  # Changed format to JSON
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./modified_test.json")  # Changed file extension to JSON
    logger.set_source(src)

    # # Analyzers
    nr_rrc_analyzer = NrRrcAnalyzer()
    nr_rrc_analyzer.set_source(src)  # bind with the monitor

    lte_rrc_analyzer = LteRrcAnalyzer()
    lte_rrc_analyzer.set_source(src)  # bind with the monitor

    lte_meas_analyzer = LteMeasurementAnalyzer()
    lte_meas_analyzer.set_source(src)

    # Perform additional analysis
    rsrp_list = lte_meas_analyzer.get_rsrp_list()
    rsrq_list = lte_meas_analyzer.get_rsrq_list()

    # Calculate average RSRP and RSRQ
    avg_rsrp = sum(rsrp_list) / len(rsrp_list) if rsrp_list else None
    avg_rsrq = sum(rsrq_list) / len(rsrq_list) if rsrq_list else None

    print("Average RSRP:", avg_rsrp)
    print("Average RSRQ:", avg_rsrq)

    # Start the monitoring
    src.run()
