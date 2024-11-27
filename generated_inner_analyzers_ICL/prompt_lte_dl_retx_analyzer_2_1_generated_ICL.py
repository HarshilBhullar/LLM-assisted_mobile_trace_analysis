
#!/usr/bin/python
# Filename: lte_dl_retx_analyzer_modified.py
"""
lte_dl_retx_analyzer_modified.py
An analyzer to calculate average MAC and RLC retransmission delays with adjusted metrics
"""

__all__ = ["LteDlRetxAnalyzerModified"]

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from mobile_insight.analyzer.analyzer import *

class LteDlRetxAnalyzerModified(Analyzer):
    """
    An analyzer to calculate average MAC and RLC retransmission delays
    """
    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)
        self.bearer_entity = {}

    def set_source(self, source):
        """
        Set the trace source. Enable the RLC logs

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)
        source.enable_log("LTE_RLC_UL_AM_All_PDU")
        source.enable_log("LTE_RLC_DL_AM_All_PDU")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_RLC_UL_AM_All_PDU":
            self.__msg_rlc_ul_callback(msg)
        elif msg.type_id == "LTE_RLC_DL_AM_All_PDU":
            self.__msg_rlc_dl_callback(msg)

    def __msg_rlc_ul_callback(self, msg):
        log_item = msg.data.decode()
        for rb_cfg in log_item['Subpackets']:
            rb_id = rb_cfg['RB Cfg Index']
            if rb_id not in self.bearer_entity:
                self.bearer_entity[rb_id] = RadioBearerEntityModified(rb_id)
            self.bearer_entity[rb_id].process_ul_rlc_pdu(log_item['timestamp'], rb_cfg)

    def __msg_rlc_dl_callback(self, msg):
        log_item = msg.data.decode()
        for rb_cfg in log_item['Subpackets']:
            rb_id = rb_cfg['RB Cfg Index']
            if rb_id not in self.bearer_entity:
                self.bearer_entity[rb_id] = RadioBearerEntityModified(rb_id)
            self.bearer_entity[rb_id].process_dl_rlc_pdu(log_item['timestamp'], rb_cfg)


class RadioBearerEntityModified:
    """
    Handle RLC data and control PDUs for each radio bearer
    """
    def __init__(self, rb_id):
        self.rb_id = rb_id
        self.mac_retx = []
        self.rlc_retx = []
        self.received_packets = []
        self.disorder_packets = []
        self.nack_packets = []
        self.loss_times = []

    def process_ul_rlc_pdu(self, timestamp, rb_cfg):
        for pdu in rb_cfg['RLCDL PDUs']:
            if pdu['PDU TYPE'] == 'RLCUL DATA':
                self.__process_received_rlc_data_pdu(timestamp, pdu)
            elif pdu['PDU TYPE'] == 'RLCUL CONTROL':
                self.__process_received_rlc_control_pdu(timestamp, pdu)

    def process_dl_rlc_pdu(self, timestamp, rb_cfg):
        for pdu in rb_cfg['RLCUL PDUs']:
            if pdu['PDU TYPE'] == 'RLCDL DATA':
                self.__process_received_rlc_data_pdu(timestamp, pdu)
            elif pdu['PDU TYPE'] == 'RLCDL CONTROL':
                self.__process_received_rlc_control_pdu(timestamp, pdu)

    def __process_received_rlc_data_pdu(self, timestamp, pdu):
        seq_num = pdu['SN']
        if seq_num not in self.received_packets:
            self.received_packets.append(seq_num)
        else:
            delay = self.__calculate_delay(timestamp, seq_num)
            self.rlc_retx.append({'rlc_retx': delay})

    def __process_received_rlc_control_pdu(self, timestamp, pdu):
        for nack in pdu['NACK']:
            seq_num = nack['NACK_SN']
            if seq_num not in self.nack_packets:
                self.nack_packets.append(seq_num)
            else:
                delay = self.__calculate_delay(timestamp, seq_num)
                self.mac_retx.append({'mac_retx': delay})

    def __calculate_delay(self, timestamp, seq_num):
        # Placeholder for actual delay calculation logic
        return 0  # Replace this with actual delay computation
