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
        self.rbInfo = {}
        self.startThrw = None

    def set_source(self, source):
        """
        Set the trace source. Enable the LTE RLC UL messages

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)
        source.enable_log("LTE_RLC_UL_AM_All_PDU")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_RLC_UL_AM_All_PDU":
            log_item = msg.data.decode()

            if self.startThrw is None:
                self.startThrw = log_item['timestamp']

            subPkt = log_item['Subpackets'][0]
            rbConfigIdx = subPkt['RB Cfg Idx']

            if rbConfigIdx not in self.rbInfo:
                self.rbInfo[rbConfigIdx] = {
                    'cumulativeULData': 0,
                    'cumulativeDLData': 0,
                    'UL': {'listSN': [], 'listAck': []},
                    'DL': {'listSN': [], 'listAck': []}
                }

            listPDU = subPkt['RLCUL PDUs']
            for pdu in listPDU:
                self.rbInfo[rbConfigIdx]['cumulativeULData'] += pdu['pdu_bytes']

    def report_throughput(self, time_window):
        print("Uplink sent throughput")
        for k, v in self.rbInfo.items():
            print(f"RB Cfg Idx: {k}, {v['cumulativeULData'] / time_window} bytes/s")
            self.rbInfo[k]['cumulativeULData'] = 0.0

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
    time_window = 1  # seconds
    analyzer.report_throughput(time_window)