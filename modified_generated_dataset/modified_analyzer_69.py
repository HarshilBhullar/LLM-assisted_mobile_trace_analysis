
#!/usr/bin/python

import sys
import csv

from mobile_insight.monitor import OfflineReplayer

__all__ = ["ModifiedAnalyzer"]

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from mobile_insight.analyzer.analyzer import *

class ModifiedAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)
        self.new_attach = False
        self.messages = []

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
                        self.messages.append(('attach_accept', data["timestamp"]))
        elif msg.type_id == "LTE_RRC_OTA_Packet":
            data = msg.data.decode()
            if "log_msg_len" in data and data["log_msg_len"]==33:
                self.messages.append(('rrc_release', data["timestamp"]))
            elif "log_msg_len" in data and data["log_msg_len"]==40:
                self.messages.append(('rrc_conn_req', data["timestamp"]))
        elif msg.type_id == "LTE_NAS_EMM_OTA_Outgoing_Packet":
            data = msg.data.decode()
            if 'Msg' in data.keys():
                log_xml = ET.XML(data['Msg'])
            else:
                return
            xml_msg = Event(msg.timestamp, msg.type_id, log_xml)
            for field in xml_msg.data.iter('field'):
                if field.get('name') != None and 'nas_eps.nas_msg' in field.get('name'):
                    if field.get('showname') == 'NAS EPS Mobility Management Message Type: Control plane service request (0x4d)':
                        self.messages.append(('ctrl_pln_svc_req', data["timestamp"]))

def modified_analysis(input_path):

    src = OfflineReplayer()
    src.set_input_path(input_path)

    analyzer = ModifiedAnalyzer()
    analyzer.set_source(src)
    try:
        src.run()
    except:
        print('Failed:', input_path)
        return None

    return analyzer


input_path = sys.argv[1]
analyzer = modified_analysis(input_path)
if analyzer:
    processed_messages = []
    for message in analyzer.messages:
        processed_messages.append(message)

    # Calculate differences with a different metric
    for i, msg in enumerate(processed_messages):
        if msg[0] == 'ctrl_pln_svc_req':
            # Find the closest rrc_release before it
            closest_rrc_release = max((m for m in processed_messages[:i] if m[0] == 'rrc_release'), default=None, key=lambda x: x[1])
            # Find the closest rrc_conn_req after it
            closest_rrc_conn_req = min((m for m in processed_messages[i+1:] if m[0] == 'rrc_conn_req'), default=None, key=lambda x: x[1])
            
            if closest_rrc_release and closest_rrc_conn_req:
                # Calculate the elapsed time since the last attach_accept before rrc_release
                last_attach_accept = max((m for m in processed_messages[:i] if m[0] == 'attach_accept'), default=None, key=lambda x: x[1])
                if last_attach_accept:
                    elapsed_time = closest_rrc_release[1] - last_attach_accept[1]
                    with open('elapsed_time_stats.csv', 'a') as f:
                        row = [input_path, elapsed_time]
                        writer = csv.writer(f)
                        writer.writerow(row)
