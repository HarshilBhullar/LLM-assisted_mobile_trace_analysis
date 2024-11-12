
#!/usr/bin/python

import sys
import csv

from mobile_insight.monitor import OfflineReplayer

__all__ = ["myModifiedAnalyzer"]

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from mobile_insight.analyzer.analyzer import *

class myModifiedAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)
        self.rrc_conn_reqs = []
        self.rrc_releases = []

    def set_source(self, source):
        """
        Set the trace source. Enable the cellular signaling messages

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)
        source.enable_log("LTE_NAS_EMM_OTA_Incoming_Packet")
        source.enable_log("LTE_NAS_EMM_OTA_Outgoing_Packet")
        source.enable_log("LTE_RRC_OTA_Packet")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_NAS_EMM_OTA_Incoming_Packet":
            data = msg.data.decode()
            if 'Msg' in data.keys():
                log_xml = ET.XML(data['Msg'])
            else:
                return
            xml_msg = Event(msg.timestamp, msg.type_id, log_xml)
            for field in xml_msg.data.iter('field'):
                if field.get('name') != None and 'nas_eps.nas_msg' in field.get('name'):
                    if field.get('showname') == 'NAS EPS Mobility Management Message Type: Attach accept (0x42)':
                        # Just to showcase a change, we are not using Attach accept in the modified version
                        pass
        elif msg.type_id == "LTE_RRC_OTA_Packet":
            data = msg.data.decode()
            if "log_msg_len" in data and data["log_msg_len"]==33:
                self.rrc_releases.append(data["timestamp"])
            elif "log_msg_len" in data and data["log_msg_len"]==40:
                self.rrc_conn_reqs.append(data["timestamp"])

def my_modified_analysis(input_path):

    src = OfflineReplayer()
    src.set_input_path(input_path)

    analyzer = myModifiedAnalyzer()
    analyzer.set_source(src)
    try:
        src.run()
    except:
        print('Failed:', input_path)
        return None

    return analyzer

input_path = sys.argv[1]
analyzer = my_modified_analysis(input_path)
if analyzer:
    # Calculate time intervals between pairs of RRC Connection Requests and RRC Releases
    with open('modified_interval_stats.csv', 'a') as f:
        writer = csv.writer(f)
        for release_time in analyzer.rrc_releases:
            # Find the closest RRC Connection Request after the RRC Release
            closest_conn_req = min((req for req in analyzer.rrc_conn_reqs if req > release_time), default=None, key=lambda x: x)
            if closest_conn_req:
                difference = closest_conn_req - release_time
                row = [input_path, release_time, closest_conn_req, difference]
                writer.writerow(row)
