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
        self.rrc_release = False
        self.rrc_conn_req = False
        self.messages = []

    def set_source(self, source):
        """
        Set the trace source. Enable the cellular signaling messages
            :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)
        #source.enable_log("LTE_NAS_ESM_OTA_Incoming_Packet")
        #source.enable_log("LTE_NAS_ESM_OTA_Outgoing_Packet")
        source.enable_log("LTE_NAS_EMM_OTA_Incoming_Packet")
        source.enable_log("LTE_NAS_EMM_OTA_Outgoing_Packet")
        source.enable_log("LTE_RRC_OTA_Packet")
        # source.enable_log_all()

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_NAS_EMM_OTA_Incoming_Packet":
            data = msg.data.decode()
            if 'Msg' in data.keys():
                log_xml = ET.XML(data['Msg'])
                #print('x')
            else:
                return
            xml_msg = Event(msg.timestamp, msg.type_id, log_xml)
            for field in xml_msg.data.iter('field'):
                if field.get('name') != None and 'nas_eps.nas_msg' in field.get('name'):
                    if field.get('showname') == 'NAS EPS Mobility Management Message Type: Attach accept (0x42)':
                        self.messages.append(('attach_accept', data["timestamp"]))
                    elif field.get('showname') == 'NAS EPS Mobility Management Message Type: Authentication request (0x52)':
                        self.messages.append(('auth_request', data["timestamp"]))
                    elif field.get('showname') == 'NAS EPS Mobility Management Message Type: Security mode command (0x5d)':
                        self.messages.append(('sec_cmd', data["timestamp"]))
                    elif field.get('showname') == 'NAS EPS Mobility Management Message Type: Attach reject (0x44)':
                        self.messages.append(('attach_rej', data["timestamp"]))
        elif msg.type_id == "LTE_RRC_OTA_Packet":
            data = msg.data.decode()
            if "log_msg_len" in data and data["log_msg_len"]==33:
                self.messages.append(('rrc_release', data["timestamp"]))
            elif "log_msg_len" in data and data["log_msg_len"]==40:
                self.messages.append(('rrc_conn_req', data["timestamp"]))
        elif msg.type_id == "LTE_NAS_EMM_OTA_Outgoing_Packet":
            data = msg.data.decode()
            if 'Msg' in data.keys():
                log_xml = ET.XML(data['Msg'])
            else:
                return
            xml_msg = Event(msg.timestamp, msg.type_id, log_xml)
            for field in xml_msg.data.iter('field'):
                if field.get('name') != None and 'nas_eps.nas_msg' in field.get('name'):
                    if field.get('showname') == 'NAS EPS Mobility Management Message Type: Attach request (0x41)':
                        self.messages.append(('attach_req', data["timestamp"]))

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
    counts = {msg_type: len([msg for msg in analyzer.messages if msg[0] == msg_type]) for msg_type in ['auth_request', 'sec_cmd', 'attach_accept', 'attach_req', 'attach_rej']}
    with open('attach_stats.csv', 'a') as f:
        row = [input_path] + [counts[msg_type] for msg_type in ['auth_request', 'sec_cmd', 'attach_accept', 'attach_req', 'attach_rej']]
        writer = csv.writer(f)
        writer.writerow(row)