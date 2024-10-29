
#!/usr/bin/python
# Filename: modified-offline-analysis.py

import os
import sys

"""
Modified Offline analysis by replaying logs with enhanced metrics and processing
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, NrRrcAnalyzer, LteRrcAnalyzer, LteMeasurementAnalyzer

if __name__ == "__main__":

    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")

    # Enable specific logs for analysis
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    # Setup a message logger with JSON format for better readability
    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.JSON)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./enhanced_test.json")
    logger.set_source(src)

    # Initialize analyzers and bind them to the monitor
    nr_rrc_analyzer = NrRrcAnalyzer()
    nr_rrc_analyzer.set_source(src)

    lte_rrc_analyzer = LteRrcAnalyzer()
    lte_rrc_analyzer.set_source(src)

    # Introduce LteMeasurementAnalyzer to process additional metrics
    lte_meas_analyzer = LteMeasurementAnalyzer()
    lte_meas_analyzer.set_source(src)
    
    # New data processing: Calculate average RSRP and RSRQ
    def calculate_average_metric(metric_list):
        return sum(metric_list) / len(metric_list) if metric_list else None
    
    # Start the monitoring
    src.run()

    # Fetch and print enhanced metrics
    rsrp_list = lte_meas_analyzer.get_rsrp_list()
    rsrq_list = lte_meas_analyzer.get_rsrq_list()

    avg_rsrp = calculate_average_metric(rsrp_list)
    avg_rsrq = calculate_average_metric(rsrq_list)

    print("Average RSRP:", avg_rsrp)
    print("Average RSRQ:", avg_rsrq)

### Key Modifications:

# 1. **Output Format Change**: The `MsgLogger` now uses JSON format (`MsgLogger.JSON`) for improved readability and modern data handling.

# 2. **Additional Analyzer**: The `LteMeasurementAnalyzer` is included and used to extract and calculate additional metrics like average RSRP and RSRQ.

# 3. **New Data Processing**: A function, `calculate_average_metric`, is introduced to compute the average of the RSRP and RSRQ lists, enabling a more insightful analysis of signal quality.

# 4. **Consistent Structure**: The code maintains consistency with the original codebase in terms of structure, logging, and initialization procedures, ensuring it integrates smoothly with existing components.