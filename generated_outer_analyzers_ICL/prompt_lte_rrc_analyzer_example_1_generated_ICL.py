
#!/usr/bin/python
# Filename: modified-offline-analysis-example.py
import os
import sys

"""
Modified offline analysis by replaying logs
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, LteRrcAnalyzer

class ModifiedLteRrcAnalyzer(LteRrcAnalyzer):
    def __init__(self):
        super().__init__()
        self.add_source_callback(self.__custom_callback)

    def __custom_callback(self, msg):
        if msg.type_id == "MEAS_PCELL":
            rsrp = msg.data.get('rsrp', None)
            rsrq = msg.data.get('rsrq', None)
            if rsrp is not None and rsrq is not None:
                sqi = self.calculate_sqi(rsrp, rsrq)
                print(f"Signal Quality Index (SQI): {sqi}")

    def calculate_sqi(self, rsrp, rsrq):
        # Example calculation of SQI
        return rsrp + (rsrq / 2.0)

if __name__ == "__main__":

    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")
    # src.enable_log_all()

    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_Serv_Cell_Info")
    src.enable_log("LTE_RRC_CDRX_Events_Info")

    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./modified_test.txt")
    logger.set_source(src)

    modified_lte_rrc_analyzer = ModifiedLteRrcAnalyzer()
    modified_lte_rrc_analyzer.set_source(src)  # bind with the monitor

    # Start the monitoring
    src.run()
