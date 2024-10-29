
#!/usr/bin/python

import sys
import csv

from mobile_insight.monitor import OfflineReplayer

__all__ = ["EnhancedAnalyzer"]

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from mobile_insight.analyzer.analyzer import *


import time


class EnhancedAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)
        self.auth_count = 0
        self.security_count = 0
        self.attach_accept_count = 0
        self.attach_request_count = 0 #Outgoing
        self.attach_reject_count = 0
        self.total_messages = 0

    def set_source(self, source):
        """
        Set the trace source. Enable the cellular signaling messages

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)
        source.enable_log("LTE_NAS_ESM_OTA_Incoming_Packet")
        source.enable_log("LTE_NAS_ESM_OTA_Outgoing_Packet")
        source.enable_log("LTE_NAS_EMM_OTA_Incoming_Packet")
        source.enable_log("LTE_NAS_EMM_OTA_Outgoing_Packet")
        # source.enable_log("LTE_RRC_OTA_Packet")
        # source.enable_log_all()    

    def reset_counter(self):
        self.auth_count = 0
        self.security_count = 0
        self.attach_accept_count = 0
        self.attach_request_count = 0
        self.attach_reject_count = 0
        self.total_messages = 0 

    def __msg_callback(self, msg):
        self.total_messages += 1
        if msg.type_id == "LTE_NAS_ESM_OTA_Incoming_Packet" or msg.type_id == "LTE_NAS_EMM_OTA_Incoming_Packet":
            data = msg.data.decode()
            if 'Msg' in data.keys():
                log_xml = ET.XML(data['Msg'])
            else:
                return
            xml_msg = Event(msg.timestamp, msg.type_id, log_xml)
            for field in xml_msg.data.iter('field'):
                if field.get('name') != None and 'nas_eps.nas_msg' in field.get('name'):
                    if field.get('showname') == 'NAS EPS Mobility Management Message Type: Attach accept (0x42)':
                        self.attach_accept_count += 1
                    elif field.get('showname') == 'NAS EPS Mobility Management Message Type: Attach reject (0x44)':
                        self.attach_reject_count += 1
                    elif field.get('showname') == 'NAS EPS Mobility Management Message Type: Authentication request (0x52)':
                        self.auth_count += 1
                    elif field.get('showname') == 'NAS EPS Mobility Management Message Type: Security mode command (0x5d)':
                        self.security_count += 1
        elif msg.type_id == "LTE_NAS_ESM_OTA_Outgoing_Packet" or msg.type_id == "LTE_NAS_EMM_OTA_Outgoing_Packet":
            data = msg.data.decode()
            if 'Msg' in data.keys():
                log_xml = ET.XML(data['Msg'])
            else:
                return
            xml_msg = Event(msg.timestamp, msg.type_id, log_xml)
            for field in xml_msg.data.iter('field'):
                if field.get('name') != None and 'nas_eps.nas_msg' in field.get('name'):
                    if field.get('showname') == 'NAS EPS Mobility Management Message Type: Attach request (0x41)':
                        self.attach_request_count += 1

    def get_message_statistics(self):
        return {
            'auth_count': self.auth_count,
            'security_count': self.security_count,
            'attach_accept_count': self.attach_accept_count,
            'attach_request_count': self.attach_request_count,
            'attach_reject_count': self.attach_reject_count,
            'total_messages': self.total_messages
        }


def enhanced_analysis(input_path):

    src = OfflineReplayer()
    src.set_input_path(input_path)

    analyzer = EnhancedAnalyzer()
    analyzer.set_source(src)
    try:
        src.run()
    except:
        print('Failed:', input_path)
        return None

    return analyzer


input_path = sys.argv[1]
analyzer = enhanced_analysis(input_path)
if analyzer:
    stats = analyzer.get_message_statistics()
    row = [input_path, stats['auth_count'], stats['security_count'], stats['attach_accept_count'], stats['attach_request_count'], stats['attach_reject_count'], stats['total_messages']]
    with open('enhanced_attach_stats.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(row)
