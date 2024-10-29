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
        self.idle_to_dch_count = 0
        self.dch_to_idle_count = 0

    def set_source(self, source):
        """
        Set the trace source. Enable the cellular signaling messages

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)
        source.enable_log("WCDMA_RRC_States")

    def __msg_callback(self, msg):
        if msg.type_id == "WCDMA_RRC_States":
            current_state = init_state(msg)
            if current_state == 'IDLE':
                if to_dch(msg):
                    self.idle_to_dch_count += 1
            elif current_state == 'DCH':
                if to_idle(msg):
                    self.dch_to_idle_count += 1

def to_dch(msg):
    for field in msg.data.iter('field'):
        if field.get('name') == "rrc.rrcConnectionSetup":
            return True
    return False

def to_idle(msg):
    for field in msg.data.iter('field'):
        if field.get('name') == "rrc.rrcConnectionRelease":
            return True
    return False

def init_state(msg):
    if msg.type_id == "WCDMA_RRC_States":
        state = 'IDLE' if str(msg.data['RRC State']) == 'DISCONNECTED' else str(msg.data['RRC State'])
        return state

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
    row = [input_path, analyzer.idle_to_dch_count, analyzer.dch_to_idle_count]
    with open('state_transition_stats.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(row)
