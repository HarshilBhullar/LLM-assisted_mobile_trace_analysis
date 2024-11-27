
from mobile_insight.analyzer import Analyzer

class RadioBearerEntityModified:
    def __init__(self):
        self.packets = {}
        self.mac_retx = []
        self.rlc_retx = []
        self.retx_count = 0

    def process_packet(self, pdu_type, sequence_number, sys_frame_number, sub_frame_number):
        key = (pdu_type, sequence_number)
        timestamp = sys_frame_number * 10 + sub_frame_number

        if key in self.packets:
            delay = timestamp - self.packets[key]
            if pdu_type == 'MAC':
                self.mac_retx.append({'mac_retx': delay})
            elif pdu_type == 'RLC':
                self.rlc_retx.append({'rlc_retx': delay})
            self.retx_count += 1
        else:
            self.packets[key] = timestamp


class LteDlRetxAnalyzerModified(Analyzer):
    def __init__(self):
        super().__init__()
        self.bearer_entity = {}

    def set_source(self, source):
        source.enable_log("LTE_RLC_UL_AM_All_PDU")
        source.enable_log("LTE_RLC_DL_AM_All_PDU")
        self.source = source
        self.source.set_callback(self.__msg_callback)

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_RLC_DL_AM_All_PDU":
            self.__process_rlc_dl(msg)
        elif msg.type_id == "LTE_RLC_UL_AM_All_PDU":
            self.__process_rlc_ul(msg)

    def __process_rlc_dl(self, msg):
        log_item = msg.data.decode()
        sys_frame_number = log_item['Sys Frame Number']
        sub_frame_number = log_item['Sub Frame Number']

        for pdu in log_item['PDUs']:
            rb_id = pdu['RB Id']
            sequence_number = pdu['SN']

            if rb_id not in self.bearer_entity:
                self.bearer_entity[rb_id] = RadioBearerEntityModified()

            self.bearer_entity[rb_id].process_packet('RLC', sequence_number, sys_frame_number, sub_frame_number)

    def __process_rlc_ul(self, msg):
        log_item = msg.data.decode()
        sys_frame_number = log_item['Sys Frame Number']
        sub_frame_number = log_item['Sub Frame Number']

        for pdu in log_item['PDUs']:
            rb_id = pdu['RB Id']
            sequence_number = pdu['SN']

            if rb_id not in self.bearer_entity:
                self.bearer_entity[rb_id] = RadioBearerEntityModified()

            self.bearer_entity[rb_id].process_packet('MAC', sequence_number, sys_frame_number, sub_frame_number)
