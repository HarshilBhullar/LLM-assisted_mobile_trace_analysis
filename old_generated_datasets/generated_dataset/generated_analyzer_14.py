#!/usr/bin/python

import sys
import csv

from mobile_insight.monitor import OfflineReplayer

__all__ = ["myKpiAnalyzer"]

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from mobile_insight.analyzer.analyzer import *

class myKpiAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)
        self.attach_reject_count = 0
        self.attach_fail_count = 0
        self.handover_states = []

    def set_source(self, source):
        """
        Set the trace source. Enable the LTE EMM messages

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)
        source.enable_log("LTE_NAS_EMM_OTA_Incoming_Packet")
        source.enable_log("LTE_NAS_EMM_OTA_Outgoing_Packet")
        source.enable_log("LTE_RRC_OTA_Packet")

    def __msg_callback(self, msg):
        log_item = msg.data.decode()
        log_item_dict = dict(log_item)

        if msg.type_id == "LTE_NAS_EMM_OTA_Incoming_Packet":
            if 'Msg' in log_item_dict:
                log_xml = ET.XML(log_item_dict['Msg'])
                for field in log_xml.iter('field'):
                    if field.get('name') != None and 'nas_eps.nas_msg' in field.get('name'):
                        if field.get('showname') == 'NAS EPS Mobility Management Message Type: Attach reject (0x44)':
                            self.attach_reject_count += 1
                        elif field.get('showname') == 'NAS EPS Mobility Management Message Type: Authentication failure (0x5c)':
                            self.attach_fail_count += 1
        elif msg.type_id == "LTE_RRC_OTA_Packet" and 'Msg' in log_item_dict:
            log_xml = ET.XML(log_item_dict['Msg'])
            for field in log_xml.iter('field'):
                if field.get('name') == 'lte-rrc.mobilityControlInfo_element':
                    for item in field.iter('field'):
                        if item.get('name') == 'lte-rrc.targetPhysCellId':
                            self.handover_states.append(item.get('show'))
                            break

def my_kpi_analysis(input_path):

    src = OfflineReplayer()
    src.set_input_path(input_path)

    analyzer = myKpiAnalyzer()
    analyzer.set_source(src)
    try:
        src.run()
    except:
        print('Failed:', input_path)
        return None

    return analyzer


input_path = sys.argv[1]
analyzer = my_kpi_analysis(input_path)
if analyzer:
    row = [input_path, analyzer.attach_reject_count, analyzer.attach_fail_count, len(analyzer.handover_states)]
    with open('kpi_stats.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(row)
