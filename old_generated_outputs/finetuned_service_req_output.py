#!/usr/bin/python

import sys
import os
import csv
import time
from datetime import datetime
from dateutil import tz

from mobile_insight.analyzer.analyzer import *

class myAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)
        
        self.service_rej_counter = 0
        self.service_accept_counter = 0
        self.control_plane_service_request_counter = 0
        self.rrc_release_counter = 0

    def reset_counter(self):
        self.service_rej_counter = 0
        self.service_accept_counter = 0
        self.control_plane_service_request_counter = 0
        self.rrc_release_counter = 0

    def __msg_callback(self,msg):

        data = msg.data.decode()
        
        if msg.type_id == "LTE_NAS_EMM_OTA_Incoming_Packet" or msg.type_id == "LTE_NAS_EMM_OTA_Outgoing_Packet":
            if "Log packet len" in data:  # For log packets
                if "NasMsg" in data["Log packet len"]:
                    #print('NAS_MSG:',data["Log packet len"]["NasMsg"])
                    if 'Msg' in data['Log packet len']["NasMsg"]:
                        #print(data['Log packet len']["NasMsg"]['Msg'])
                        for item in data['Log packet len']["NasMsg"]['Msg']:
                            if 'Data' in item and 'LteNasEmmMessageType' in item: #Some log packets (eg: settings) might not have Data field
                                if item['LteNasEmmMessageType'] == "ServiceRequest":
                                    self.control_plane_service_request_counter += 1
                                if item['LteNasEmmMessageType'] == "ServiceAccept":
                                    self.service_accept_counter += 1
                                if item['LteNasEmmMessageType'] == "ServiceReject":
                                    self.service_rej_counter += 1

                            if 'Msg' in item and 'LteNasEmmMessageType' in item: #Some log packets (eg: settings) might not have Data field
                                if item['LteNasEmmMessageType'] == "ServiceRequest":
                                    self.control_plane_service_request_counter += 1
                                if item['LteNasEmmMessageType'] == "ServiceAccept":
                                    self.service_accept_counter += 1
                                if item['LteNasEmmMessageType'] == "ServiceReject":
                                    self.service_rej_counter += 1
                                    
                
            if 'Subpackets' in data:
                for subpacket in data['Subpackets']:
                    if "NasMsg" in subpacket:
                        #print('NAS_MSG:',subpacket["NasMsg"])
                        if 'Msg' in subpacket["NasMsg"]:
                            #print(subpacket["NasMsg"]['Msg'])
                            for item in subpacket["NasMsg"]['Msg']:
                                if 'Data' in item and 'LteNasEmmMessageType' in item: #Some log packets (eg: settings) might not have Data field
                                    if item['LteNasEmmMessageType'] == "ServiceRequest":
                                        self.control_plane_service_request_counter += 1
                                    if item['LteNasEmmMessageType'] == "ServiceAccept":
                                        self.service_accept_counter += 1
                                    if item['LteNasEmmMessageType'] == "ServiceReject":
                                        self.service_rej_counter += 1
                                
                                if 'Msg' in item and 'LteNasEmmMessageType' in item: #Some log packets (eg: settings) might not have Data field
                                    if item['LteNasEmmMessageType'] == "ServiceRequest":
                                        self.control_plane_service_request_counter += 1
                                    if item['LteNasEmmMessageType'] == "ServiceAccept":
                                        self.service_accept_counter += 1
                                    if item['LteNasEmmMessageType'] == "ServiceReject":
                                        self.service_rej_counter += 1
                                    

        if msg.type_id == "LTE_RRC_OTA_Packet":
            if "Messages" in data:
                for msg_item in data['Messages']:
                    if 'rrc Connection Release' in msg_item:
                        if 'length' in msg_item:
                            print('log_msg_len:', msg_item['length'])
                        else: 
                            print('Length key not found')
                        print('timestamp:',msg_item['timestamp'])
        


#DfAnalyzer.listen_to_those_with_const_fields({'LteNasEmmCause':'6'})
#DfAnalyzer.remove_source(LteRrcOtaAnalyzer1)
#DfAnalyzer.remove_source(LteNasEmmAnalyzer2)
#DfAnalyzer.remove_source(LteNasEmmAnalyzer3)
#DfAnalyzer.remove_source(LteMacAnalyzer4)
#DfAnalyzer.remove_source(LtePhyAnalyzer5)
#DfAnalyzer.remove_source(LtePdcpAnalyzer6)
#DfAnalyzer.remove_source(LteRlcAnalyzer7)
#DfAnalyzer.remove_source(WcdmaRrcAnalyzer8)
#DfAnalyzer.remove_source(UmtsNasAnalyzer9)
#DfAnalyzer.remove_source(UmtsLayer23Analyzer10)
#DfAnalyzer.remove_source(UmtsLayer1Analyzer11)
#DfAnalyzer.remove_source(UmtsMacAnalyzer12)
#DfAnalyzer.remove_source(UmtsRlcAnalyzer13)
#DfAnalyzer.remove_source(GsmBtsAnalyzer14)
#DfAnalyzer.remove_source(GsmMsAnalyzer15)
#DfAnalyzer.remove_source(GsmMobileAnalyzer16)
#DfAnalyzer.remove_source(GsmACommonAnalyzer17)
#DfAnalyzer.remove_source(GsmAbisAnalyzer18)
#DfAnalyzer.remove_source(GsmPdtchAnalyzer19)
#DfAnalyzer.remove_source(LtePhyAnalyzer20)
#DfAnalyzer.remove_source(LteMacAnalyzer21)
#DfAnalyzer.remove_source(LteRlcAnalyzer22)
#DfAnalyzer.remove_source(LtePdcpAnalyzer23)
#DfAnalyzer.remove_source(Layer1Analyzer24)

def my_analysis(input_path): 
    
    src = OfflineReplayer()
    my_analyzer=myAnalyzer()

    src.set_input_path(input_path)
    #print(dir(src))
    #print(dir(my_analyzer))
    #src.enable_log_all()
    #src.enable_log("LTE_RRC_OTA_Packet")
    src.add_analyzer(my_analyzer)
    try:
        #print('OMG')
        src.run()
        #print('Ran?')
    except:
        print('exception encountered:',input_path)
        return None

    return my_analyzer

if __name == '__main__':    
    input_path = sys.argv[1]    
    analyzer = my_analysis(input_path)
    if analyzer!=None:
        print(analyzer.rrc_release_counter)
        if analyzer.control_plane_service_request_counter and (analyzer.service_rej_counter or analyzer.service_accept_counter):
            with open('myAnalysis.csv', 'a') as csvfile:
                analyser_data = [input_path, analyzer.control_plane_service_request_counter, analyzer.service_accept_counter, analyzer.service_rej_counter]
                print(analyser_data)
                writer = csv.writer(csvfile)
                writer.writerows([analyser_data])
