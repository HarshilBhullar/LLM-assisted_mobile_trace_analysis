
#!/usr/bin/python

import sys
import csv

from mobile_insight.monitor import OfflineReplayer

__all__ = ["modifiedAnalyzer"]

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from mobile_insight.analyzer.analyzer import *

class modifiedAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)
        self.attach_request_count = 0
        self.service_rej_count = 0
        self.service_accept_count = 0
        self.rrc_release_count = 0

    def set_source(self, source):
        """
        Set the trace source. Enable the cellular signaling messages

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)
        source.enable_log("LTE_NAS_EMM_OTA_Incoming_Packet")
        source.enable_log("LTE_NAS_EMM_OTA_Outgoing_Packet")
        source.enable_log("LTE_RRC_OTA_Packet")

    def reset_counter(self):
        self.attach_request_count = 0
        self.service_rej_count = 0
        self.service_accept_count = 0
        self.rrc_release_count = 0

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_NAS_EMM_OTA_Incoming_Packet":
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
                    elif field.get('showname') == 'NAS EPS Mobility Management Message Type: Service accept (0x4f)':
                        self.service_accept_count += 1
                    elif field.get('showname') == 'NAS EPS Mobility Management Message Type: Service reject (0x4e)':
                        self.service_rej_count += 1
        elif msg.type_id == "LTE_RRC_OTA_Packet":
            data = msg.data.decode()
            if "log_msg_len" in data:
                print(data["log_msg_len"])
            if "timestamp" in data:
                print(data["timestamp"])
        elif msg.type_id == "LTE_NAS_EMM_OTA_Outgoing_Packet":
            data = msg.data.decode()
            if 'Msg' in data.keys():
                log_xml = ET.XML(data['Msg'])
            else:
                return
            xml_msg = Event(msg.timestamp, msg.type_id, log_xml)
            for field in xml_msg.data.iter('field'):
                if field.get('name') != None and 'nas_eps.nas_msg' in field.get('name'):
                    if field.get('showname') == 'NAS EPS Mobility Management Message Type: Control plane service request (0x4d)':
                        self.service_accept_count += 1

def modified_analysis(input_path):

    src = OfflineReplayer()
    src.set_input_path(input_path)

    analyzer = modifiedAnalyzer()
    analyzer.set_source(src)
    try:
        src.run()
    except:
        print('Failed:', input_path)
        return None

    return analyzer


input_path = sys.argv[1]
analyzer = modified_analysis(input_path)
if analyzer:
    print(analyzer.rrc_release_count)
    if analyzer.attach_request_count >= 1 and (analyzer.service_accept_count + analyzer.service_rej_count) >= 1:
        with open('service_req_stats.csv', 'a') as f:
            row = [input_path, analyzer.attach_request_count, analyzer.service_accept_count, analyzer.service_rej_count]
            writer = csv.writer(f)
            writer.writerow(row)
