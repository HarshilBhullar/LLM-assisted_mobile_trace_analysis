#!/usr/bin/python

import sys
import csv

from mobile_insight.monitor import OfflineReplayer

__all__ = ["LatencyAnalyzer"]

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from mobile_insight.analyzer.analyzer import *

class LatencyAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)
        self.total_latency = 0
        self.total_wait = 0
        self.total_trans = 0
        self.total_retx = 0
        self.packet_count = 0

    def set_source(self, source):
        """
        Set the trace source. Enable the cellular signaling messages

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)
        source.enable_log("LTE_NAS_EMM_OTA_Incoming_Packet")
        source.enable_log("LTE_NAS_EMM_OTA_Outgoing_Packet")
        source.enable_log("LTE_RRC_OTA_Packet")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_NAS_EMM_OTA_Incoming_Packet" or msg.type_id == "LTE_NAS_EMM_OTA_Outgoing_Packet":
            data = msg.data.decode()
            if 'Msg' in data.keys():
                log_xml = ET.XML(data['Msg'])
            else:
                return
            xml_msg = Event(msg.timestamp, msg.type_id, log_xml)
            for field in xml_msg.data.iter('field'):
                if field.get('name') != None and 'lte_rrc.packet_latency' in field.get('name'):
                    self.total_latency += int(field.get('value'))
                    if 'waiting' in field.get('showname'):
                        self.total_wait += int(field.get('value'))
                    elif 'transmission' in field.get('showname'):
                        self.total_trans += int(field.get('value'))
                    elif 'retransmission' in field.get('showname'):
                        self.total_retx += int(field.get('value'))
                    self.packet_count += 1

def my_analysis(input_path):

    src = OfflineReplayer()
    src.set_input_path(input_path)

    analyzer = LatencyAnalyzer()
    analyzer.set_source(src)
    try:
        src.run()
    except:
        print('Failed:', input_path)
        return None

    return analyzer


input_path = sys.argv[1]
analyzer = my_analysis(input_path)
if analyzer and analyzer.packet_count > 0:
    with open('latency_stats.csv', 'a') as f:
        writer = csv.writer(f)
        row = [
            input_path,
            float(analyzer.total_latency) / analyzer.packet_count,
            float(analyzer.total_wait) / analyzer.packet_count,
            float(analyzer.total_trans) / analyzer.packet_count,
            float(analyzer.total_retx) / analyzer.packet_count
        ]
        writer.writerow(row)
else:
    print("No valid packets found or failed to analyze:", input_path)
