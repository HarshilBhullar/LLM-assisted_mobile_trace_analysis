#!/usr/bin/python

import sys
import csv
import re

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
        self.qci_info = {}
        self.meas_report_seq = MeasReportSeq()

    def set_source(self, source):
        """
        Set the trace source. Enable the cellular signaling messages

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)
        source.enable_log("LTE_NAS_EMM_OTA_Incoming_Packet")
        source.enable_log("LTE_RRC_OTA_Packet")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_NAS_EMM_OTA_Incoming_Packet":
            data = msg.data.decode()
            if 'Msg' in data.keys():
                log_xml = ET.XML(data['Msg'])
            else:
                return
            for field in log_xml.iter('field'):
                if field.get('name') == "nas_eps.emm.qci":
                    qci_value = field.get('showname').split(":")[1].strip()
                    self.qci_info[msg.timestamp] = qci_value
        elif msg.type_id == "LTE_RRC_OTA_Packet":
            data = msg.data.decode()
            if 'Msg' in data.keys():
                log_xml = ET.XML(data['Msg'])
            else:
                return
            for field in log_xml.iter('field'):
                if field.get('name') == "nr-rrc.reportConfigNR_element":
                    cur_pair = ("dummy_meas_obj", "dummy_report_config")
                    self.meas_report_seq.add_meas_report(cur_pair)

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
    with open('qci_stats.csv', 'a') as f:
        writer = csv.writer(f)
        for timestamp, qci in analyzer.qci_info.items():
            row = [input_path, timestamp, qci]
            writer.writerow(row)

    with open('meas_report_stats.csv', 'a') as f:
        writer = csv.writer(f)
        for report in analyzer.meas_report_seq.meas_report_queue:
            row = [input_path, report]
            writer.writerow(row)