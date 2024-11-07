
#!/usr/bin/python

import sys
import csv

from mobile_insight.monitor import OfflineReplayer

__all__ = ["myModifiedAnalyzer"]

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from mobile_insight.analyzer.analyzer import *


import time


class myModifiedAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)
        self.auth_count = 0
        self.security_count = 0
        self.attach_accept_count = 0
        self.attach_request_count = 0 #Outgoing
        self.attach_reject_count = 0
        self.total_messages = 0  # New metric to track total messages processed

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

    def reset_counter(self):
        self.auth_count = 0
        self.security_count = 0
        self.attach_accept_count = 0
        self.attach_request_count = 0
        self.attach_reject_count = 0
        self.total_messages = 0

    def __msg_callback(self, msg):
        self.total_messages += 1  # Increment the total message counter
        if msg.type_id in ["LTE_NAS_ESM_OTA_Incoming_Packet", "LTE_NAS_EMM_OTA_Incoming_Packet"]:
            data = msg.data.decode()
            if 'Msg' in data.keys():
                log_xml = ET.XML(data['Msg'])
            else:
                return
            xml_msg = Event(msg.timestamp, msg.type_id, log_xml)
            for field in xml_msg.data.iter('field'):
                if field.get('name') is not None and 'nas_eps.nas_msg' in field.get('name'):
                    if field.get('showname') == 'NAS EPS Mobility Management Message Type: Attach accept (0x42)':
                        self.attach_accept_count += 1
                    elif field.get('showname') == 'NAS EPS Mobility Management Message Type: Attach reject (0x44)':
                        self.attach_reject_count += 1
                    elif field.get('showname') == 'NAS EPS Mobility Management Message Type: Authentication request (0x52)':
                        self.auth_count += 1
                    elif field.get('showname') == 'NAS EPS Mobility Management Message Type: Security mode command (0x5d)':
                        self.security_count += 1
        elif msg.type_id in ["LTE_NAS_ESM_OTA_Outgoing_Packet", "LTE_NAS_EMM_OTA_Outgoing_Packet"]:
            data = msg.data.decode()
            if 'Msg' in data.keys():
                log_xml = ET.XML(data['Msg'])
            else:
                return
            xml_msg = Event(msg.timestamp, msg.type_id, log_xml)
            for field in xml_msg.data.iter('field'):
                if field.get('name') is not None and 'nas_eps.nas_msg' in field.get('name'):
                    if field.get('showname') == 'NAS EPS Mobility Management Message Type: Attach request (0x41)':
                        self.attach_request_count += 1

    def calculate_message_ratios(self):
        """Calculate and return the ratio of each message type to the total messages."""
        if self.total_messages == 0:
            return 0, 0, 0, 0, 0
        auth_ratio = self.auth_count / self.total_messages
        security_ratio = self.security_count / self.total_messages
        attach_accept_ratio = self.attach_accept_count / self.total_messages
        attach_request_ratio = self.attach_request_count / self.total_messages
        attach_reject_ratio = self.attach_reject_count / self.total_messages
        return auth_ratio, security_ratio, attach_accept_ratio, attach_request_ratio, attach_reject_ratio


def my_modified_analysis(input_path):
    src = OfflineReplayer()
    src.set_input_path(input_path)

    analyzer = myModifiedAnalyzer()
    analyzer.set_source(src)
    try:
        src.run()
    except:
        print('Failed:', input_path)
        return None

    return analyzer


input_path = sys.argv[1]
analyzer = my_modified_analysis(input_path)
if analyzer:
    auth_ratio, security_ratio, attach_accept_ratio, attach_request_ratio, attach_reject_ratio = analyzer.calculate_message_ratios()
    row = [input_path, analyzer.auth_count, analyzer.security_count, analyzer.attach_accept_count, analyzer.attach_request_count, analyzer.attach_reject_count,
           auth_ratio, security_ratio, attach_accept_ratio, attach_request_ratio, attach_reject_ratio]
    with open('attach_stats_modified.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(row)
