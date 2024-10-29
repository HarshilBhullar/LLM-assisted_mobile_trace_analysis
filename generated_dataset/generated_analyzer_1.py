#!/usr/bin/python

import sys
import csv

from mobile_insight.monitor import OfflineReplayer

__all__ = ["BandwidthAnalyzer"]

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from mobile_insight.analyzer.analyzer import *


class BandwidthAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)
        self.total_bandwidth = 0
        self.count = 0

    def set_source(self, source):
        """
        Set the trace source. Enable the cellular signaling messages

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)
        source.enable_log("LTE_PHY_PDSCH_Stat_Indication")
        # source.enable_log_all()

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_PHY_PDSCH_Stat_Indication":
            data = msg.data.decode()
            if 'log_item' in data.keys():
                log_item = data['log_item']
                bandwidth = log_item.get('Bandwidth (Mbps)', None)
                if bandwidth:
                    self.total_bandwidth += float(bandwidth)
                    self.count += 1

    def get_average_bandwidth(self):
        if self.count == 0:
            return 0
        return self.total_bandwidth / self.count


def my_analysis(input_path):

    src = OfflineReplayer()
    src.set_input_path(input_path)

    analyzer = BandwidthAnalyzer()
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
    average_bandwidth = analyzer.get_average_bandwidth()
    with open('bandwidth_stats.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow([input_path, average_bandwidth])


### Explanation:
# This new analyzer, `BandwidthAnalyzer`, focuses on calculating the average downlink bandwidth from LTE PHY PDSCH statistics. It interprets the `LTE_PHY_PDSCH_Stat_Indication` messages to sum up the available bandwidth and compute an average over the duration of the trace. The results are then logged into a CSV file, `bandwidth_stats.csv`, where each entry contains the input path and the computed average bandwidth. This functionality utilizes available bandwidth data from the library snippets, showcasing a unique feature of analyzing and reporting bandwidth statistics.