
#!/usr/bin/python
# Filename: modified-offline-analysis-example.py
import os
import sys

"""
Modified offline analysis by replaying logs
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, LteDlRetxAnalyzer

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

    lte_dl_retx_analyzer = LteDlRetxAnalyzer()
    lte_dl_retx_analyzer.set_source(src)

    # Custom processing: Calculate retx statistics
    def calculate_retx_statistics(analyzer):
        mac_retx_count = sum(len(entity.mac_retx) for entity in analyzer.bearer_entity.values())
        rlc_retx_count = sum(len(entity.rlc_retx) for entity in analyzer.bearer_entity.values())
        print(f"Total MAC retransmissions: {mac_retx_count}")
        print(f"Total RLC retransmissions: {rlc_retx_count}")

    # Start the monitoring
    src.run()

    # After running, analyze the results
    calculate_retx_statistics(lte_dl_retx_analyzer)
