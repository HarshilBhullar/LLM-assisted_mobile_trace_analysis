#!/usr/bin/python

import sys
import csv

from mobile_insight.monitor import OfflineReplayer

__all__ = ["myNewAnalyzer"]

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from mobile_insight.analyzer.analyzer import *


class myNewAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)
        self.handover_events = []

    def set_source(self, source):
        """
        Set the trace source. Enable the cellular signaling messages

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)
        source.enable_log("LTE_RRC_OTA_Packet")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_RRC_OTA_Packet":
            data = msg.data.decode()
            if 'Msg' in data.keys():
                log_xml = ET.XML(data['Msg'])
            else:
                return
            xml_msg = Event(msg.timestamp, msg.type_id, log_xml)
            for field in xml_msg.data.iter('field'):
                if field.get('name') == 'lte-rrc.eventA3_element':
                    offset = None
                    quantity = None
                    for item in field.iter('field'):
                        if item.get('name') == 'lte-rrc.a3_Offset':
                            offset = int(item.get('show')) / 2
                        if item.get('name') == 'lte-rrc.threshold_RSRP':
                            quantity = 'rsrp'
                    if offset is not None and quantity is not None:
                        self.handover_events.append((offset, quantity, msg.timestamp))


def my_analysis(input_path):

    src = OfflineReplayer()
    src.set_input_path(input_path)

    analyzer = myNewAnalyzer()
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
    with open('handover_events.csv', 'a') as f:
        writer = csv.writer(f)
        for event in analyzer.handover_events:
            row = [input_path, event[0], event[1], event[2]]
            writer.writerow(row)
