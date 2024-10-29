#!/usr/bin/python

import sys
import csv

from mobile_insight.monitor import OfflineReplayer

__all__ = ["handoffAnalyzer"]

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from mobile_insight.analyzer.analyzer import *

class handoffAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)
        self.handoff_attempts = 0
        self.handoff_success = 0
        self.current_state = None

    def set_source(self, source):
        """
        Set the trace source. Enable the cellular signaling messages

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)
        source.enable_log("LTE_RRC_OTA_Packet")
        source.enable_log("LTE_NAS_EMM_OTA_Incoming_Packet")
        source.enable_log("LTE_NAS_EMM_OTA_Outgoing_Packet")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_RRC_OTA_Packet":
            data = msg.data.decode()
            if 'Msg' in data.keys():
                log_xml = ET.XML(data['Msg'])
            else:
                return
            xml_msg = Event(msg.timestamp, msg.type_id, log_xml)
            for field in xml_msg.data.iter('field'):
                if field.get('name') == 'lte-rrc.handoverCommand':
                    self.handoff_attempts += 1
                    self.current_state = 'handoverCommand'
                elif field.get('name') == 'lte-rrc.handoverComplete' and self.current_state == 'handoverCommand':
                    self.handoff_success += 1
                    self.current_state = None

def analyze_handoff(input_path):
    src = OfflineReplayer()
    src.set_input_path(input_path)

    analyzer = handoffAnalyzer()
    analyzer.set_source(src)
    try:
        src.run()
    except:
        print('Failed:', input_path)
        return None

    return analyzer

input_path = sys.argv[1]
analyzer = analyze_handoff(input_path)
if analyzer:
    row = [input_path, analyzer.handoff_attempts, analyzer.handoff_success]
    with open('handoff_stats.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(row)
