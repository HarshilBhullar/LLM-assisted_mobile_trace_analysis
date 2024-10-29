
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

# import threading


class myModifiedAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)
        self.new_attach = False
        self.service_rej_count = 0
        self.control_plane_service_request_count = 0
        self.service_accept_count = 0
        self.rrc_release_count = 0
        self.attach_reject_count = 0  # New metric

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
        self.service_rej_count = 0
        self.control_plane_service_request_count = 0
        self.service_accept_count = 0
        self.rrc_release_count = 0
        self.attach_reject_count = 0  # Reset new metric

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
                    if field.get('showname') == 'NAS EPS Mobility Management Message Type: Attach accept (0x42)':
                        self.new_attach = True
                    if field.get('showname') == 'NAS EPS Mobility Management Message Type: Attach reject (0x44)':
                        self.attach_reject_count += 1  # Increment new metric
                    if field.get('showname') == 'NAS EPS Mobility Management Message Type: Service accept (0x4f)':
                        if not self.new_attach:
                            self.service_accept_count += 1
                        else:
                            self.new_attach = False
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
                        self.control_plane_service_request_count += 1

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
    print(analyzer.rrc_release_count)
    if analyzer.control_plane_service_request_count >= 1 and (analyzer.service_accept_count + analyzer.service_rej_count) >= 1:
        with open('service_req_stats.csv', 'a') as f:
            row = [input_path, analyzer.control_plane_service_request_count, analyzer.service_accept_count, analyzer.service_rej_count, analyzer.attach_reject_count]
            writer = csv.writer(f)
            writer.writerow(row)
