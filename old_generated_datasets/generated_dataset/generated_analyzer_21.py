#!/usr/bin/python

import sys
import csv

from mobile_insight.monitor import OfflineReplayer

__all__ = ["ThroughputAnalyzer"]

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from mobile_insight.analyzer.analyzer import *

class ThroughputAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)
        self.downlink_data = 0
        self.uplink_data = 0

    def set_source(self, source):
        """
        Set the trace source. Enable the cellular signaling messages

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)
        source.enable_log("LTE_RLC_DL_AM_All_PDU")
        source.enable_log("LTE_RLC_UL_AM_All_PDU")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_RLC_DL_AM_All_PDU":
            data = msg.data.decode()
            if 'PDU Size' in data.keys():
                self.downlink_data += int(data['PDU Size'])
        elif msg.type_id == "LTE_RLC_UL_AM_All_PDU":
            data = msg.data.decode()
            if 'PDU Size' in data.keys():
                self.uplink_data += int(data['PDU Size'])

def my_throughput_analysis(input_path):

    src = OfflineReplayer()
    src.set_input_path(input_path)

    analyzer = ThroughputAnalyzer()
    analyzer.set_source(src)
    try:
        src.run()
    except:
        print('Failed:', input_path)
        return None

    return analyzer

input_path = sys.argv[1]
analyzer = my_throughput_analysis(input_path)
if analyzer:
    row = [input_path, analyzer.downlink_data, analyzer.uplink_data]
    with open('throughput_stats.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(row)