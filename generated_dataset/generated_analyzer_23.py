#!/usr/bin/python

import sys
import csv

from mobile_insight.monitor import OfflineReplayer

__all__ = ["QciAnalyzer"]

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from mobile_insight.analyzer.analyzer import Analyzer


class QciAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)
        self.qci_counts = {'QCI1': 0, 'QCI2': 0, 'QCI3': 0, 'QCI4': 0}

    def set_source(self, source):
        """
        Set the trace source. Enable the cellular signaling messages

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)
        source.enable_log("LTE_NAS_ESM_OTA_Incoming_Packet")
        source.enable_log("LTE_NAS_ESM_OTA_Outgoing_Packet")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_NAS_ESM_OTA_Incoming_Packet" or msg.type_id == "LTE_NAS_ESM_OTA_Outgoing_Packet":
            data = msg.data.decode()
            if 'Msg' in data.keys():
                log_xml = ET.XML(data['Msg'])
            else:
                return
            xml_msg = Event(msg.timestamp, msg.type_id, log_xml)
            for field in xml_msg.data.iter('field'):
                if field.get('name') == 'eps_bearer.qci':
                    qci_value = field.get('showname').split(':')[-1].strip()
                    if qci_value in self.qci_counts:
                        self.qci_counts[qci_value] += 1

def analyze_qci(input_path):

    src = OfflineReplayer()
    src.set_input_path(input_path)

    analyzer = QciAnalyzer()
    analyzer.set_source(src)
    try:
        src.run()
    except:
        print('Failed:', input_path)
        return None

    return analyzer

input_path = sys.argv[1]
analyzer = analyze_qci(input_path)
if analyzer:
    row = [input_path, analyzer.qci_counts['QCI1'], analyzer.qci_counts['QCI2'], analyzer.qci_counts['QCI3'], analyzer.qci_counts['QCI4']]
    with open('qci_stats.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(row)