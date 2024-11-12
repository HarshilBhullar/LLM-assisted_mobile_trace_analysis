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
        self.handoff_attempts = 0
        self.handoff_successes = 0
        self.handoff_failures = 0

    def set_source(self, source):
        """
        Set the trace source. Enable the cellular signaling messages

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)
        source.enable_log("NR_RRC_OTA_Packet")

    def __msg_callback(self, msg):
        if msg.type_id == "NR_RRC_OTA_Packet":
            data = msg.data.decode()
            if 'Msg' in data.keys():
                log_xml = ET.XML(data['Msg'])
            else:
                return
            xml_msg = Event(msg.timestamp, msg.type_id, log_xml)
            for field in xml_msg.data.iter('field'):
                if field.get('name') != None and 'nr-rrc' in field.get('name'):
                    if field.get('showname') == 'NR RRC Message Type: RRC Connection Reconfiguration (0x44)':
                        self.handoff_attempts += 1
                        self.check_handoff_success_or_failure(xml_msg)

    def check_handoff_success_or_failure(self, xml_msg):
        for field in xml_msg.data.iter('field'):
            if field.get('name') != None:
                if field.get('showname') == 'NR RRC Reconfiguration Complete':
                    self.handoff_successes += 1
                elif field.get('showname') == 'NR RRC Reconfiguration Failure':
                    self.handoff_failures += 1


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
    row = [input_path, analyzer.handoff_attempts, analyzer.handoff_successes, analyzer.handoff_failures]
    with open('handoff_stats.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(row)