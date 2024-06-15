
#!/usr/bin/python

import sys
import csv

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.analyzer import *

class myAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.attach_accepts = 0
        self.attach_requests = 0
        self.attach_rejections = 0
        self.auth_requests = 0
        self.security_commands = 0
        
        self.add_source_callback(self.__msg_callback)

    def set_source(self, source):
        Analyzer.set_source(self, source)
        source.enable_log("LTE_NAS_ESM_OTA_Incoming_Packet")
        source.enable_log("LTE_NAS_ESM_OTA_Outgoing_Packet")
        source.enable_log("LTE_NAS_EMM_OTA_Incoming_Packet")
        source.enable_log("LTE_NAS_EMM_OTA_Outgoing_Packet")
        
    def __msg_callback(self, msg):
        if msg.type_id == "LTE_NAS_EMM_OTA_Incoming_Packet":
            data = msg.data.decode()
            if 'Msg' in data.keys():
                log_xml = ET.XML(data['Msg'])
            else:
                return
            xml_msg = Event(msg.timestamp, msg.type_id, log_xml)
            for field in xml_msg.data.iter('field'):
                if field.get('name') != None:
                    if 'nas_eps.nas_msg' in field.get('name'):
                        if field.get('showname') == 'NAS EPS Mobility Management Message Type: Attach accept (0x42)':
                            self.attach_accepts += 1
                        elif field.get('showname') == 'NAS EPS Mobility Management Message Type: Attach request (0x41)':
                            self.attach_requests += 1
                        elif field.get('showname') == 'NAS EPS Mobility Management Message Type: Attach reject (0x43)':
                            self.attach_rejections += 1
                        elif field.get('showname') == 'NAS EPS Authentication Request':
                            self.auth_requests += 1
        elif msg.type_id == "LTE_NAS_EMM_OTA_Outgoing_Packet":
            data = msg.data.decode()
            if 'Msg' in data.keys():
                log_xml = ET.XML(data['Msg'])
            else:
                return
            xml_msg = Event(msg.timestamp, msg.type_id, log_xml)
            for field in xml_msg.data.iter('field'):
                if field.get('name') != None:
                    if 'nas_eps.nas_msg' in field.get('name'):
                        if field.get('ShowName') == 'NAS EPS Mobility Management Message Type: Security mode Command (0x2d)':
                            self.security_commands += 1

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
    stats = [input_path, analyzer.auth_requests, analyzer.security_commands, analyzer.attach_accepts, analyzer.attach_requests, analyzer.attach_rejections]
    with open('attach_stats.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(stats)
  