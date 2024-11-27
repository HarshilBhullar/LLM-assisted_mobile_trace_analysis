
#!/usr/bin/python
# Filename: lte_dl_retx_modified_analyzer.py
"""
A modified analyzer to monitor downlink MAC retransmission delay and RLC retransmission delay with enhanced calculations.

Author: Qianru Li (Modified)
"""

from mobile_insight.analyzer.analyzer import Analyzer
import datetime

__all__ = ["LteDlRetxModifiedAnalyzer"]


def comp_seq_num(s1, s2):
    if s1 == s2:
        return 0
    if (s2 - s1 + 1024) % 1024 <= 150:  # Assuming a max sequence number of 1024
        return -1
    return 1


class RadioBearerEntity:
    def __init__(self, num):
        self.__idx = num
        self.__pkt_recv = []  # a list of first-received packet, in ascending order
        self.__pkt_disorder = []
        self.__max_sn = -1
        self.__nack_dict = {}  # sn:[nack_time,timestamp]; a list of nack packet; w/o retx
        self.__loss_detected_time = {}  # sn:[loss_detected_time,timestamp]
        self.mac_retx = []
        self.rlc_retx = []

    def recv_rlc_data(self, pdu, timestamp):
        if 'LSF' in pdu and pdu['LSF'] == 0:
            return

        sys_time = pdu['sys_fn'] * 10 + pdu['sub_fn']
        sn = pdu['SN']

        # Process RLC data PDU
        if sn not in self.__pkt_recv:
            self.__pkt_recv.append(sn)
        else:
            if sn not in self.rlc_retx:
                self.rlc_retx.append({'rlc_retx': sys_time - self.__loss_detected_time.get(sn, sys_time)})
        
        if sn in self.__nack_dict:
            nack_time = self.__nack_dict[sn][0]
            self.mac_retx.append({'mac_retx': sys_time - nack_time})
            del self.__nack_dict[sn]

    def recv_rlc_ctrl(self, pdu, timestamp):
        sn = pdu['SN']
        nack_time = pdu['timestamp']
        self.__nack_dict[sn] = [nack_time, timestamp]


class LteDlRetxModifiedAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.bearer_entity = {}
        self.add_source_callback(self.__msg_callback)

    def set_source(self, source):
        """
        Set the trace source. Enable the LTE RLC UL and DL AM PDU messages.

        :param source: the trace source.
        :type source: trace collector
        """
        Analyzer.set_source(self, source)
        source.enable_log("LTE_RLC_UL_AM_All_PDU")
        source.enable_log("LTE_RLC_DL_AM_All_PDU")

    def __msg_callback(self, msg):
        log_item = msg.data.decode()

        if msg.type_id == "LTE_RLC_UL_AM_All_PDU":
            self.__process_ul_pdu(log_item, msg.timestamp)
        elif msg.type_id == "LTE_RLC_DL_AM_All_PDU":
            self.__process_dl_pdu(log_item, msg.timestamp)

    def __process_ul_pdu(self, log_item, timestamp):
        for pdu in log_item['PDUs']:
            if pdu['RBID'] not in self.bearer_entity:
                self.bearer_entity[pdu['RBID']] = RadioBearerEntity(pdu['RBID'])

            entity = self.bearer_entity[pdu['RBID']]
            if pdu['PDU TYPE'] == "RLCUL DATA":
                entity.recv_rlc_data(pdu, timestamp)
            elif pdu['PDU TYPE'] == "RLCUL CTRL":
                entity.recv_rlc_ctrl(pdu, timestamp)

    def __process_dl_pdu(self, log_item, timestamp):
        for pdu in log_item['PDUs']:
            if pdu['RBID'] not in self.bearer_entity:
                self.bearer_entity[pdu['RBID']] = RadioBearerEntity(pdu['RBID'])

            entity = self.bearer_entity[pdu['RBID']]
            if pdu['PDU TYPE'] == "RLCDL DATA":
                entity.recv_rlc_data(pdu, timestamp)
            elif pdu['PDU TYPE'] == "RLCDL CTRL":
                entity.recv_rlc_ctrl(pdu, timestamp)
