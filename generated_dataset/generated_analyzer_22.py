#!/usr/bin/python

import sys
import csv

from mobile_insight.monitor import OfflineReplayer

__all__ = ["myUniqueAnalyzer"]

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from mobile_insight.analyzer.analyzer import *


class myUniqueAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)
        self.pdp_context_count = 0
        self.qos_updates = []

    def set_source(self, source):
        """
        Set the trace source. Enable the necessary cellular signaling messages

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)
        source.enable_log("UMTS_NAS_OTA_Packet")
        source.enable_log("UMTS_NAS_GMM_State")
        
    def __msg_callback(self, msg):
        if msg.type_id == "UMTS_NAS_OTA_Packet":
            data = msg.data.decode()
            if 'Msg' in data.keys():
                log_xml = ET.XML(data['Msg'])
            else:
                return
            xml_msg = Event(msg.timestamp, msg.type_id, log_xml)
            for field in xml_msg.data.iter('field'):
                if field.get('name') and 'nas_umts.gmm.message_type' in field.get('name'):
                    if field.get('showname') == 'UMTS GMM Message Type: PDP Context Activation Request (0x41)':
                        self.pdp_context_count += 1
                elif field.get('name') and 'nas_umts.qos' in field.get('name'):
                    qos_info = self.extract_qos_info(field)
                    self.qos_updates.append((msg.timestamp, qos_info))

    def extract_qos_info(self, field):
        qos_info = {}
        for sub_field in field.iter('field'):
            if sub_field.get('name'):
                qos_info[sub_field.get('name')] = sub_field.get('showname')
        return qos_info


def my_unique_analysis(input_path):

    src = OfflineReplayer()
    src.set_input_path(input_path)

    analyzer = myUniqueAnalyzer()
    analyzer.set_source(src)
    try:
        src.run()
    except:
        print('Failed:', input_path)
        return None

    return analyzer


input_path = sys.argv[1]
analyzer = my_unique_analysis(input_path)
if analyzer:
    with open('qos_stats.csv', 'a') as f:
        writer = csv.writer(f)
        for timestamp, qos_info in analyzer.qos_updates:
            row = [input_path, timestamp] + list(qos_info.values())
            writer.writerow(row)
    print(f"PDP Context Activation Requests: {analyzer.pdp_context_count}")