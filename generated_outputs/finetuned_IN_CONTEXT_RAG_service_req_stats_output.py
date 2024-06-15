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
        self.service_rejects = 0
        self.service_accepts = 0
        self.ctrl_pln_svc_reqs = 0
        self.rrc_releases = 0
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
            else:
                return
            xml_msg = Event(msg.timestamp, msg.type_id, log_xml)
            for field in xml_msg.data.iter('field'):
                if field.get('name') != None and 'nas_eps.nas_msg' in field.get('name'):
                    if field.get('showname') == 'NAS EPS Mobility Management Message Type: Service reject (0x5)':
                        self.service_rejects += 1
                    elif field.get('showname') == 'NAS EPS Mobility Management Message Type: Service accept (0x6)':
                        self.service_accepts += 1
                    elif field.get('showname') == 'NAS EPS Mobility Management Message Type: Control plane service request (0x4d)':
                        self.ctrl_pln_svc_reqs += 1
        elif msg.type_id == "LTE_RRC_OTA_Packet":
            data = msg.data.decode()
            if "log_msg_len" in data:
                print(data["log_msg_len"], data["timestamp"])
                if data["log_msg_len"] == 33:
                    self.messages.append(('rrc_release', data["timestamp"]))


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
    print(analyzer.rrc_releases)
    if analyzer.ctrl_pln_svc_reqs > 0 and (analyzer.service_accepts > 0 or analyzer.service_rejects > 0):
        with open('service_stats.csv', 'a') as f:
            row = [input_path, analyzer.ctrl_pln_svc_reqs, analyzer.service_accepts, analyzer.service_rejects]
            writer = csv.writer(f)
            writer.writerow(row)