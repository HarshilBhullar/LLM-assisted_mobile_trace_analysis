#!/usr/bin/python

import sys
import csv

from mobile_insight.monitor import OfflineReplayer

__all__ = ["myAnalyzer"]

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from mobile_insight.analyzer.analyzer import *


class myAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)
        self.pdcp_integrity_failures = 0
        self.rrc_connection_events = []

    def set_source(self, source):
        """
        Set the trace source. Enable the cellular signaling messages

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)
        source.enable_log("LTE_PDCP_UL_SRB_Integrity_Data_PDU")
        source.enable_log("LTE_RRC_OTA_Packet")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_PDCP_UL_SRB_Integrity_Data_PDU":
            log_item = msg.data.decode()
            if 'Integrity check failed' in log_item.get('Status', ''):
                self.pdcp_integrity_failures += 1

        elif msg.type_id == "LTE_RRC_OTA_Packet":
            log_item = msg.data.decode()
            if 'lte-rrc.rrcConnectionSetupComplete_element' in log_item.get('Msg', ''):
                self.rrc_connection_events.append(('setup_complete', msg.timestamp))
            elif 'lte-rrc.rrcConnectionRelease_element' in log_item.get('Msg', ''):
                self.rrc_connection_events.append(('release', msg.timestamp))

def my_analysis(input_path):

    src = OfflineReplayer()
    src.set_input_path(input_path)

    analyzer = myAnalyzer()
    analyzer.set_source(src)
    try:
        src.run()
    except:
        print('Failed:', input_path)
        return None

    return analyzer


input_path = sys.argv[1]
analyzer = my_analysis(input_path)
if analyzer:
    with open('integrity_rrc_stats.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(['Input Path', 'PDCP Integrity Failures', 'RRC Connection Events'])
        writer.writerow([input_path, analyzer.pdcp_integrity_failures, len(analyzer.rrc_connection_events)])