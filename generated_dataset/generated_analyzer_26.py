```python
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
        self.ul_throughput_events = []

    def set_source(self, source):
        """
        Set the trace source. Enable the cellular signaling messages

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)
        source.enable_log("LTE_PHY_PDSCH_Stat_Indication")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_PHY_PDSCH_Stat_Indication":
            data = msg.data.decode()
            if 'PDSCH_Stat' in data.keys():
                pdsch_stats = data['PDSCH_Stat']
                for stat in pdsch_stats:
                    if 'Throughput' in stat:
                        self.ul_throughput_events.append((msg.timestamp, stat['Throughput']))

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
    with open('ul_throughput_stats.csv', 'a') as f:
        writer = csv.writer(f)
        for event in analyzer.ul_throughput_events:
            row = [input_path, event[0], event[1]]
            writer.writerow(row)
```