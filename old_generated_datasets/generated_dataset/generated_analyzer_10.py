#!/usr/bin/python

import sys
import csv

from mobile_insight.monitor import OfflineReplayer

__all__ = ["QoSAnalyzer"]

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from mobile_insight.analyzer.analyzer import *

class QoSAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)
        self.qos_records = []

    def set_source(self, source):
        """
        Set the trace source. Enable the cellular signaling messages

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)
        source.enable_log("LTE_NAS_ESM_OTA_Incoming_Packet")
        source.enable_log("LTE_NAS_ESM_OTA_Outgoing_Packet")

    def __msg_callback(self, msg):
        if msg.type_id in ["LTE_NAS_ESM_OTA_Incoming_Packet", "LTE_NAS_ESM_OTA_Outgoing_Packet"]:
            data = msg.data.decode()
            if 'Msg' in data.keys():
                log_xml = ET.XML(data['Msg'])
            else:
                return
            for field in log_xml.iter('field'):
                if field.get('name') and 'qos' in field.get('name'):
                    qos_info = {
                        'timestamp': msg.timestamp,
                        'precedence_class': None,
                        'peak_throughput': None,
                        'mean_throughput': None,
                        'traffic_class': None
                    }
                    for subfield in field.iter('field'):
                        if 'gsm_a.gm.sm.qos.prec_class' in subfield.get('name'):
                            qos_info['precedence_class'] = int(subfield.get('show'))
                        elif 'gsm_a.gm.sm.qos.peak_throughput' in subfield.get('name'):
                            qos_info['peak_throughput'] = 1000 * pow(2, int(subfield.get('show')))
                        elif 'gsm_a.gm.sm.qos.mean_throughput' in subfield.get('name'):
                            qos_info['mean_throughput'] = int(subfield.get('show'))
                        elif 'gsm_a.gm.sm.qos.traffic_cls' in subfield.get('name'):
                            qos_info['traffic_class'] = int(subfield.get('show'))
                    self.qos_records.append(qos_info)

def analyze_qos(input_path):

    src = OfflineReplayer()
    src.set_input_path(input_path)

    analyzer = QoSAnalyzer()
    analyzer.set_source(src)
    try:
        src.run()
    except:
        print('Failed:', input_path)
        return None

    return analyzer


input_path = sys.argv[1]
analyzer = analyze_qos(input_path)
if analyzer:
    with open('qos_stats.csv', 'a') as f:
        writer = csv.writer(f)
        for record in analyzer.qos_records:
            row = [
                input_path,
                record['timestamp'],
                record['precedence_class'],
                record['peak_throughput'],
                record['mean_throughput'],
                record['traffic_class']
            ]
            writer.writerow(row)
