
#!/usr/bin/python
# Filename: lte_dl_retx_modified_analyzer.py

from .analyzer import *
from collections import defaultdict

__all__ = ["LteDlRetxModifiedAnalyzer"]

class LteDlRetxModifiedAnalyzer(Analyzer):
    """
    An analyzer to monitor downlink MAC and RLC retransmission delay
    with enhanced calculations.
    """

    def __init__(self):
        Analyzer.__init__(self)
        self.bearer_entity = defaultdict(self.RadioBearerEntity)
        self.add_source_callback(self.__msg_callback)

    def set_source(self, source):
        """
        Set the trace source. Enable the RLC logs.

        :param source: the trace source.
        :type source: trace collector
        """
        Analyzer.set_source(self, source)

        source.enable_log("LTE_RLC_UL_AM_All_PDU")
        source.enable_log("LTE_RLC_DL_AM_All_PDU")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_RLC_UL_AM_All_PDU":
            self.__process_ul_am(msg.data.decode())
        elif msg.type_id == "LTE_RLC_DL_AM_All_PDU":
            self.__process_dl_am(msg.data.decode())

    def __process_ul_am(self, log_item):
        rb_id = log_item['rb_cfg_idx']
        if rb_id not in self.bearer_entity:
            self.bearer_entity[rb_id] = self.RadioBearerEntity(rb_id)
        self.bearer_entity[rb_id].recv_rlc_data(log_item)

    def __process_dl_am(self, log_item):
        rb_id = log_item['rb_cfg_idx']
        if rb_id not in self.bearer_entity:
            self.bearer_entity[rb_id] = self.RadioBearerEntity(rb_id)
        self.bearer_entity[rb_id].recv_rlc_ctrl(log_item)

    class RadioBearerEntity:
        def __init__(self, rb_id):
            self.rb_id = rb_id
            self.mac_retx = []
            self.rlc_retx = []
            self.received_packets = {}
            self.out_of_order = defaultdict(list)
            self.nacks = {}

        def recv_rlc_data(self, log_item):
            seq_num = log_item['SN']
            ts = log_item['Sys FN'] * 10 + log_item['Sub FN']
            if seq_num not in self.received_packets:
                self.received_packets[seq_num] = ts
            else:
                delay = ts - self.received_packets[seq_num]
                self.mac_retx.append({'mac_retx': delay - 1})  # Adjust for enhanced calculation

        def recv_rlc_ctrl(self, log_item):
            ack_sn = log_item['Ack_SN']
            for nack_sn in log_item.get('NACK_SN', []):
                if nack_sn not in self.nacks:
                    self.nacks[nack_sn] = log_item['Sys FN'] * 10 + log_item['Sub FN']
                else:
                    delay = (log_item['Sys FN'] * 10 + log_item['Sub FN']) - self.nacks[nack_sn]
                    self.rlc_retx.append({'rlc_retx': delay})
