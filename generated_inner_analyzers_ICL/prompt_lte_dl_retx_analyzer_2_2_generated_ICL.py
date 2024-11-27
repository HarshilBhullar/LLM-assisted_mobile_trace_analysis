
#!/usr/bin/python
# Filename: lte_dl_retx_analyzer_modified.py
"""
A modified analyzer to track downlink MAC and RLC retransmission delays

Author: Yuanjie Li, Modified by OpenAI
"""

from mobile_insight.analyzer.analyzer import *

__all__ = ["LteDlRetxAnalyzerModified"]

class RadioBearerEntityModified:
    def __init__(self):
        self.received_packets = []
        self.mac_retx = []
        self.rlc_retx = []
        self.retx_count = 0

    def process_packet(self, seq_num, timestamp, layer, delay):
        if layer == "MAC":
            self.mac_retx.append({'timestamp': timestamp, 'mac_retx': delay})
        elif layer == "RLC":
            self.rlc_retx.append({'timestamp': timestamp, 'rlc_retx': delay})
        self.retx_count += 1

class LteDlRetxAnalyzerModified(Analyzer):

    def __init__(self):
        Analyzer.__init__(self)
        self.bearer_entity = {}

        self.add_source_callback(self.__msg_callback)

    def set_source(self, source):
        Analyzer.set_source(self, source)
        source.enable_log("LTE_RLC_UL_AM_All_PDU")
        source.enable_log("LTE_RLC_DL_AM_All_PDU")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_RLC_UL_AM_All_PDU" or msg.type_id == "LTE_RLC_DL_AM_All_PDU":
            log_item = msg.data.decode()
            self.__process_rlc_message(log_item)

    def __process_rlc_message(self, log_item):
        if 'Subpackets' in log_item:
            for subpacket in log_item['Subpackets']:
                if 'RLCDL PDUs' in subpacket:
                    for pdu in subpacket['RLCDL PDUs']:
                        self.__process_pdu(pdu, log_item['timestamp'], "DL")
                if 'RLCUL PDUs' in subpacket:
                    for pdu in subpacket['RLCUL PDUs']:
                        self.__process_pdu(pdu, log_item['timestamp'], "UL")

    def __process_pdu(self, pdu, timestamp, direction):
        rb_id = pdu.get('RB Cfg Id', None)
        if rb_id is not None:
            if rb_id not in self.bearer_entity:
                self.bearer_entity[rb_id] = RadioBearerEntityModified()

            entity = self.bearer_entity[rb_id]
            seq_num = pdu.get('SN', None)
            retx_count = pdu.get('ReTx Count', 0)
            if retx_count > 0:
                delay = self.__calculate_delay(seq_num, retx_count)
                layer = "RLC" if direction == "DL" else "MAC"
                entity.process_packet(seq_num, timestamp, layer, delay)

    def __calculate_delay(self, seq_num, retx_count):
        return retx_count * 10  # Example calculation, modify as needed
