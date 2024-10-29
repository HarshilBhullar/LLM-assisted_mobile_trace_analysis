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
        self.esm_messages = []

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
                if field.get('name') != None and 'nas_eps.nas_msg' in field.get('name'):
                    self.esm_messages.append((field.get('showname'), data["timestamp"]))

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
    esm_message_types = {}
    for message in analyzer.esm_messages:
        msg_type = message[0]
        if msg_type in esm_message_types:
            esm_message_types[msg_type] += 1
        else:
            esm_message_types[msg_type] = 1

    with open('esm_message_stats.csv', 'a') as f:
        writer = csv.writer(f)
        for msg_type, count in esm_message_types.items():
            row = [input_path, msg_type, count]
            writer.writerow(row)
