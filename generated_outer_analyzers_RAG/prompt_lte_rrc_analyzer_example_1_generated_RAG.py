
#!/usr/bin/python
# Filename: modified-offline-analysis-example.py
import os
import sys

"""
Modified offline analysis by replaying logs
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger
from lte_rrc_analyzer import LteRrcAnalyzer

class ModifiedLteRrcAnalyzer(LteRrcAnalyzer):
    def __init__(self):
        super().__init__()

    def __callback_sib_config(self, msg):
        super().__callback_sib_config(msg)
        # Additional processing for Signal Quality Index (SQI), based on RSRP and RSRQ
        for field in msg.data.iter('field'):
            if field.get('name') == 'lte-rrc.measResultPCell_element':
                rsrp = None
                rsrq = None
                for val in field.iter('field'):
                    if val.get('name') == 'lte-rrc.rsrpResult':
                        rsrp = int(val.get('show'))
                    elif val.get('name') == 'lte-rrc.rsrqResult':
                        rsrq = int(val.get('show'))
                if rsrp is not None and rsrq is not None:
                    # SQI calculation example (this is a simplistic example and may not reflect real-world calculations)
                    sqi = (rsrp - 140) + (rsrq / 2.0 - 20)
                    self.log_info('SQI: ' + str(sqi))
                    self.broadcast_info('SQI', {'sqi': sqi})

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
    logger.save_decoded_msg_as("./decoded_messages.txt")
    logger.set_source(src)

    modified_lte_rrc_analyzer = ModifiedLteRrcAnalyzer()
    modified_lte_rrc_analyzer.set_source(src)

    # Start the monitoring
    src.run()
