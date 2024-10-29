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
        self.cell_fach_count = 0
        self.cell_dch_count = 0
        self.ura_pch_count = 0
        self.state_changes = []

    def set_source(self, source):
        """
        Set the trace source. Enable the WCDMA RRC messages

        :param source: the trace source.
        """
        Analyzer.set_source(self, source)
        source.enable_log("WCDMA_RRC_OTA_Packet")
        source.enable_log("WCDMA_RRC_States")

    def __msg_callback(self, msg):
        if to_cell_fach(msg):
            self.cell_fach_count += 1
            self.state_changes.append(('CELL_FACH', msg.timestamp))
        elif to_cell_dch(msg):
            self.cell_dch_count += 1
            self.state_changes.append(('CELL_DCH', msg.timestamp))
        elif to_ura_pch(msg):
            self.ura_pch_count += 1
            self.state_changes.append(('URA_PCH', msg.timestamp))

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
    with open('state_transitions.csv', 'a') as f:
        writer = csv.writer(f)
        for change in analyzer.state_changes:
            row = [input_path, change[0], change[1]]
            writer.writerow(row)
    row = [input_path, analyzer.cell_fach_count, analyzer.cell_dch_count, analyzer.ura_pch_count]
    with open('state_counts.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(row)