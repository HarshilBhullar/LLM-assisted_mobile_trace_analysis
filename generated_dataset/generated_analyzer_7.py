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
        self.bearer_setup_count = 0
        self.qci_types = set()

    def set_source(self, source):
        """
        Set the trace source. Enable the cellular signaling messages

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)
        source.enable_log("LTE_NAS_ESM_OTA_Incoming_Packet")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_NAS_ESM_OTA_Incoming_Packet":
            log_item = msg.data.decode()
            log_item_dict = dict(log_item)
            if 'Msg' in log_item_dict:
                log_xml = ET.XML(log_item_dict['Msg'])
                act_bearer_flag = False
                for field in log_xml.iter('field'):
                    if field.get('name') == 'nas_eps.nas_msg_esm_type' and field.get('value') == 'c5':
                        act_bearer_flag = True
                    elif act_bearer_flag and field.get('name') == 'nas_eps.emm.qci':
                        qci_value = int(field.get('show'))
                        self.qci_types.add(qci_value)
                        if 0 < qci_value < 5:
                            self.bearer_setup_count += 1
                            act_bearer_flag = False

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
    row = [input_path, analyzer.bearer_setup_count, ",".join(map(str, sorted(analyzer.qci_types)))]
    with open('bearer_setup_stats.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(row)