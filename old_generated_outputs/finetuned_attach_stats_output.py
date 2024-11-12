#!/usr/bin/python

import sys
import time
from datetime import datetime
import csv
import os
# add the current path
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '../..'))

from mobile_insight.monitor import OfflineReplayer

__all__ = ["myAnalyzer"]

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
import mobile_insight.analyzer

from mobile_insight.analyzer.analyzer import *

class myAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)

        self.attach_request_count = 0
        self.attach_accept_count = 0
        self.attach_rej_count = 0
        self.auth_request_count = 0
        self.security_command_count = 0
    def reset_counter(self, top=None):
        self.attach_request_count = 0
        self.attach_accept_count = 0
        self.attach_rej_count = 0
        self.auth_request_count = 0
        self.security_command_count = 0

    def __msg_callback(self,msg):
        xml=msg.xml_obj
        buffer = msg.data.decode()
        if msg.type_id == "LTE_NAS_OTA(Incoming)":
            msg_dir = 'incoming'
        elif msg.type_id == "LTE_NAS_OTA(Outgoing)":
            msg_dir = 'outgoing'
        else:
            return
        if ('msg_dir' in locals() and
            ('msg dir='+msg_dir) in buffer):
            if 'EMM plain OTA in ' in buffer:
                msg_type='LTE_NAS_EMM_OTA_'+msg_dir+'_Packet'
            elif 'ESM plain OTA in ' in buffer:
                msg_type='LTE_NAS_ESM_OTA_'+msg_dir+'_Packet'
            else:
                return
            if 'decoded' in buffer:
                msg_str='XML'+buffer.split('XML')[-1].split(' ')[0]
                if msg_str[3:16]  in xml:
                    self.data_layer.send(('MSG', msg_type, xml[msg_str[3:16]]))
                elif msg_str[3:15] in xml:
                    self.data_layer.send(('MSG', msg_type, xml[msg_str[3:15]]))


        if msg.type_id in [
            "LTE_NAS_EMM_OTA_Incoming_Packet",
            "LTE_NAS_EMM_OTA_Outgoing_Packet",
            "LTE_NAS_ESM_OTA_Incoming_Packet",
            "LTE_NAS_ESM_OTA_Outgoing_Packet",
            ]:
            if 'Attach Complete' in buffer:
                self.attach_accept_count += 1
            elif 'Identity Request' in buffer:
                self.auth_request_count += 1
            elif 'authentication response' in buffer:
                self.auth_request_count += 1
            elif 'Attach Request' in buffer:
                self.attach_request_count += 1
            elif 'attach reject' in buffer:
                self.attach_rej_count += 1
            elif 'EMM Information' in buffer:
                self.security_command_count += 1
                if 'eps encryption' in buffer:
                    self.security_command_count += 1
                elif 'security mode command' in buffer:
                    self.security_command_count += 1


    def attach_counts(self):
        return [
            self.auth_request_count,
            self.security_command_count,
            self.attach_accept_count,
            self.attach_request_count,
            self.attach_rej_count
            ]


analyzer_class = myAnalyzer

src = OfflineReplayer()
src.set_input_path(sys.argv[1])
# print(sys.argv[1])
analyzer = analyzer_class()
src.add_analyzer(analyzer)
# print('added')
src.run()
# print('svm')

attaches = analyzer.attach_counts()

for i in range(len(attaches)):
    attaches[i] = str(attaches[i])

with open('attach_stats.csv', 'a') as csvfile:
    stats = csv.writer(csvfile)
    stats.writerow([sys.argv[1]] + attaches)