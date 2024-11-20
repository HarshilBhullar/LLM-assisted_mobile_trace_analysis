
#!/usr/bin/python
# Filename: offline-analysis-modified.py
import os
import sys

"""
Modified Offline analysis by replaying logs
"""

# Import MobileInsight modules
from mobileinsight.monitor import OfflineReplayer
from mobileinsight.analyzer import MsgLogger, LteRrcAnalyzer

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
    logger.save_decoded_msg_as("./test_modified.txt")  # Changed output file name
    logger.set_source(src)

    lte_rrc_analyzer = LteRrcAnalyzer()
    lte_rrc_analyzer.set_source(src)  # bind with the monitor

    # Custom function to calculate additional metrics
    def calculate_additional_metrics(msg):
        if msg.type_id == 'LTE_RRC_OTA_Packet':
            for field in msg.data.iter('field'):
                if field.get('name') == 'lte-rrc.rsrpResult':
                    rsrp = int(field.get('show'))
                    rsrq = int(field.get('show'))  # Assuming rsrq is also available
                    sinr = rsrp - rsrq  # Example calculation for SINR
                    print(f"Calculated SINR: {sinr}")

    # Extend the analyzer with additional metrics
    lte_rrc_analyzer.add_callback('MSG_CALLBACK', calculate_additional_metrics)

    # Start the monitoring
    src.run()
