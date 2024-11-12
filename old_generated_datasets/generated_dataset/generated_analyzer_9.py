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
        self.drx_state_changes = []

    def set_source(self, source):
        """
        Set the trace source. Enable the cellular signaling messages

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)
        source.enable_log("LTE_RRC_OTA_Packet")
        source.enable_log("LTE_PHY_Connected_Mode_Intra_Freq_Measurement")
        # source.enable_log_all()    

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_RRC_OTA_Packet":
            data = msg.data.decode()
            if 'Msg' in data.keys():
                log_xml = ET.XML(data['Msg'])
            else:
                return
            xml_msg = Event(msg.timestamp, msg.type_id, log_xml)
            for field in xml_msg.data.iter('field'):
                if field.get('name') == "lte-rrc.nr_Config_r15":
                    setup = None
                    for var in field.iter('field'):
                        if setup is None and var.get('name') == "lte-rrc.setup_element":
                            setup = True
                        if setup is None and var.get('name') == "lte-rrc.release_element":
                            setup = False
                        if setup is not None:
                            self.drx_state_changes.append((msg.timestamp, setup))
                            self.broadcast_info('DRX', {'Timestamp': str(msg.timestamp), 'DRX_State': 'Setup' if setup else 'Release'})

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
    with open('drx_state_changes.csv', 'a') as f:
        writer = csv.writer(f)
        for change in analyzer.drx_state_changes:
            row = [input_path, change[0], 'Setup' if change[1] else 'Release']
            writer.writerow(row)