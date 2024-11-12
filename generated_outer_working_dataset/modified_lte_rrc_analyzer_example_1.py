
#!/usr/bin/python
# Filename: offline-analysis-modified.py
import os
import sys

"""
Modified offline analysis for additional LTE RRC metrics
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, LteRrcAnalyzer

class ModifiedLteRrcAnalyzer(LteRrcAnalyzer):
    def __init__(self):
        super().__init__()
        print("Init Modified RRC Analyzer")

    def __callback_sib_config(self, msg):
        """
        A callback to extract configurations from System Information Blocks (SIBs),
        including the radio asssement thresholds, the preference settings, etc.
        This method is modified to include additional metrics.
        """

        for field in msg.data.iter('field'):

            if field.get('name') == 'lte-rrc.measResultPCell_element':
                meas_report = {}
                meas_report['timestamp'] = str(msg.timestamp)
                for val in field.iter('field'):
                    if val.get('name') == 'lte-rrc.rsrpResult':
                        meas_report['rsrp'] = int(val.get('show'))
                        meas_report['rssi'] = meas_report['rsrp'] - 141  # map rsrp to rssi
                    elif val.get('name') == 'lte-rrc.rsrqResult':
                        meas_report['rsrq'] = int(val.get('show'))
                        
                # Calculate a new metric: Signal Quality Index (SQI)
                if 'rsrp' in meas_report and 'rsrq' in meas_report:
                    meas_report['sqi'] = (meas_report['rsrp'] + meas_report['rsrq']) / 2
                
                self.broadcast_info('MEAS_PCELL', meas_report)
                self.log_info('MEAS_PCELL: ' + str(meas_report))
                self.send_to_coordinator(Event(msg.timestamp, 'rsrp', meas_report['rsrp']))
                self.send_to_coordinator(Event(msg.timestamp, 'rsrq', meas_report['rsrq']))

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
    logger.save_decoded_msg_as("./test_modified.txt")
    logger.set_source(src)

    modified_lte_rrc_analyzer = ModifiedLteRrcAnalyzer()
    modified_lte_rrc_analyzer.set_source(src)  # bind with the monitor

    # Start the monitoring
    src.run()
