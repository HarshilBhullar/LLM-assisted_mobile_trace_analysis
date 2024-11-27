
#!/usr/bin/python
# Filename: modified_lte_dl_retx_analyzer.py

"""
A modified LTE DL retransmission analyzer.
Author: Adapted from existing analyzers
"""

from mobile_insight.analyzer.analyzer import Analyzer

__all__ = ["ModifiedLteDlRetxAnalyzer"]

class RadioBearerEntity:
    def __init__(self):
        self.rx_seq = set()
        self.nack_seq = {}
        self.loss_times = {}
        self.mac_retx = []
        self.rlc_retx = []

    def process_rlc_data_pdu(self, sys_fn, sub_fn, pdu_size, seq_num):
        current_time = sys_fn * 10 + sub_fn
        if seq_num in self.rx_seq:
            # Retransmission detected
            retx_time = current_time - self.loss_times.get(seq_num, current_time)
            self.mac_retx.append({'mac_retx': retx_time})
        else:
            self.rx_seq.add(seq_num)
            if seq_num in self.nack_seq:
                # Calculate RLC retransmission delay
                retx_time = current_time - self.nack_seq[seq_num]
                self.rlc_retx.append({'rlc_retx': retx_time})
                del self.nack_seq[seq_num]

    def process_rlc_control_pdu(self, sys_fn, sub_fn, nack_list):
        current_time = sys_fn * 10 + sub_fn
        for nack in nack_list:
            self.nack_seq[nack] = current_time
            self.loss_times[nack] = current_time

class ModifiedLteDlRetxAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.bearer_entity = {}
        self.add_source_callback(self.__msg_callback)

    def set_source(self, source):
        Analyzer.set_source(self, source)
        source.enable_log("LTE_RLC_UL_AM_All_PDU")
        source.enable_log("LTE_RLC_DL_AM_All_PDU")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_RLC_DL_AM_All_PDU":
            self.__msg_rlc_dl_callback(msg)
        elif msg.type_id == "LTE_RLC_UL_AM_All_PDU":
            self.__msg_rlc_ul_callback(msg)

    def __msg_rlc_dl_callback(self, msg):
        log_item = msg.data.decode()
        sys_fn = int(log_item['Sys FN'])
        sub_fn = int(log_item['Sub FN'])

        for pdu in log_item['Subpackets']:
            if pdu['Direction'] == "DL":
                rb_id = pdu['RB Cfg Id']
                if rb_id not in self.bearer_entity:
                    self.bearer_entity[rb_id] = RadioBearerEntity()
                entity = self.bearer_entity[rb_id]

                for pdu_data in pdu['PDUs']:
                    seq_num = int(pdu_data['SN'])
                    pdu_size = int(pdu_data['pdu_size'])
                    entity.process_rlc_data_pdu(sys_fn, sub_fn, pdu_size, seq_num)

    def __msg_rlc_ul_callback(self, msg):
        log_item = msg.data.decode()
        sys_fn = int(log_item['Sys FN'])
        sub_fn = int(log_item['Sub FN'])

        for pdu in log_item['Subpackets']:
            if pdu['Direction'] == "UL":
                rb_id = pdu['RB Cfg Id']
                if rb_id not in self.bearer_entity:
                    self.bearer_entity[rb_id] = RadioBearerEntity()
                entity = self.bearer_entity[rb_id]

                for pdu_ctrl in pdu['PDUs']:
                    if 'NACK' in pdu_ctrl:
                        nack_list = pdu_ctrl['NACK']
                        entity.process_rlc_control_pdu(sys_fn, sub_fn, nack_list)
