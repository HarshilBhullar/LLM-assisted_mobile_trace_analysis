
#!/usr/bin/python
# Filename: lte_dl_retx_analyzer_modified.py

"""
A modified analyzer for downlink MAC and RLC retransmission delays.

Author: Assistant
"""

from mobile_insight.analyzer.analyzer import *
import datetime

__all__ = ["LteDlRetxAnalyzerModified"]

class RadioBearerEntityModified:

    def __init__(self, num):
        self.__idx = num
        self.__pkt_recv = []  # a list of first-received packets
        self.__pkt_disorder = []
        self.__max_sn = -1
        self.__nack_dict = {}  # sn: [nack_time, timestamp]
        self.__loss_detected_time = {}  # sn: [loss_detected_time, timestamp]

        self.mac_retx = []
        self.rlc_retx = []
        self.retx_count = 0

    def recv_rlc_data(self, pdu, timestamp):
        if 'LSF' in pdu and pdu['LSF'] == 0:
            return

        sys_time = pdu['sys_fn'] * 10 + pdu['sub_fn']
        sn = pdu['SN']

        if sn not in self.__pkt_recv:
            self.__pkt_recv.append(sn)
            self.__pkt_recv.sort()
        else:
            self.retx_count += 1
            delay = sys_time - self.__nack_dict.get(sn, [sys_time])[0]
            self.rlc_retx.append({'rlc_retx': delay})
            self.__nack_dict.pop(sn, None)

    def process_mac_retx(self, harq_info, timestamp):
        sn = harq_info['SN']
        if sn in self.__pkt_recv:
            self.retx_count += 1
            delay = timestamp - self.__loss_detected_time.get(sn, [timestamp])[0]
            self.mac_retx.append({'mac_retx': delay})
            self.__loss_detected_time.pop(sn, None)


class LteDlRetxAnalyzerModified(Analyzer):

    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)
        self.bearer_entity = {}

    def set_source(self, source):
        Analyzer.set_source(self, source)
        source.enable_log("LTE_RLC_UL_AM_All_PDU")
        source.enable_log("LTE_RLC_DL_AM_All_PDU")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_RLC_UL_AM_All_PDU":
            self.__process_rlc_ul(msg)
        elif msg.type_id == "LTE_RLC_DL_AM_All_PDU":
            self.__process_rlc_dl(msg)

    def __process_rlc_ul(self, msg):
        log_item = msg.data.decode()
        timestamp = msg.timestamp
        for pdu in log_item['Subpackets']:
            rb_id = pdu['RB Cfg Idx']
            if rb_id not in self.bearer_entity:
                self.bearer_entity[rb_id] = RadioBearerEntityModified(rb_id)
            self.bearer_entity[rb_id].recv_rlc_data(pdu, timestamp)

    def __process_rlc_dl(self, msg):
        log_item = msg.data.decode()
        timestamp = msg.timestamp
        for pdu in log_item['Subpackets']:
            rb_id = pdu['RB Cfg Idx']
            if rb_id not in self.bearer_entity:
                self.bearer_entity[rb_id] = RadioBearerEntityModified(rb_id)
            self.bearer_entity[rb_id].recv_rlc_data(pdu, timestamp)
