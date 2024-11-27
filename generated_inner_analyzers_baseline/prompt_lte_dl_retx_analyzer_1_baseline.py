
from mobile_insight.analyzer.analyzer import *

class RadioBearerEntity:
    def __init__(self):
        self.received_packets = {}
        self.packet_reordering = []
        self.max_seq_num = -1
        self.nack_packets = {}
        self.packet_loss_times = {}
        self.mac_retx = []
        self.rlc_retx = []

    def update_received_packets(self, seq_num, timestamp):
        if seq_num in self.received_packets:
            self.received_packets[seq_num].append(timestamp)
        else:
            self.received_packets[seq_num] = [timestamp]

    def detect_retransmission(self, seq_num, timestamp):
        if seq_num in self.received_packets:
            # Calculate MAC retransmission delay
            first_rx_time = self.received_packets[seq_num][0]
            mac_retx_delay = timestamp - first_rx_time
            self.mac_retx.append({'seq_num': seq_num, 'mac_retx': mac_retx_delay})

    def update_nack_packets(self, seq_num, timestamp):
        self.nack_packets[seq_num] = timestamp

    def check_rlc_retx(self, seq_num, timestamp):
        if seq_num in self.nack_packets:
            nack_time = self.nack_packets[seq_num]
            rlc_retx_delay = timestamp - nack_time
            self.rlc_retx.append({'seq_num': seq_num, 'rlc_retx': rlc_retx_delay})

class ModifiedLteDlRetxAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.bearer_entity = {}

    def set_source(self, source):
        Analyzer.set_source(self, source)
        self.enable_log("LTE_RLC_UL_AM_All_PDU")
        self.enable_log("LTE_RLC_DL_AM_All_PDU")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_RLC_UL_AM_All_PDU":
            self.__msg_rlc_ul_callback(msg)
        elif msg.type_id == "LTE_RLC_DL_AM_All_PDU":
            self.__msg_rlc_dl_callback(msg)

    def __msg_rlc_ul_callback(self, msg):
        pass  # Placeholder for UL logic, if needed

    def __msg_rlc_dl_callback(self, msg):
        log_item = msg.data.decode()
        for pdu in log_item['Subpackets']:
            rb_cfg_idx = pdu['RB Cfg Idx']
            if rb_cfg_idx not in self.bearer_entity:
                self.bearer_entity[rb_cfg_idx] = RadioBearerEntity()
            entity = self.bearer_entity[rb_cfg_idx]

            for pdu_item in pdu['PDUs']:
                seq_num = pdu_item['SN']
                timestamp = msg.timestamp

                if pdu_item['PDU TYPE'] == 'RLC_DATA_PDU':
                    entity.update_received_packets(seq_num, timestamp)
                    entity.detect_retransmission(seq_num, timestamp)

                elif pdu_item['PDU TYPE'] == 'RLC_CONTROL_PDU':
                    for nack in pdu_item['NACKs']:
                        nack_seq_num = nack['NACK_SN']
                        entity.update_nack_packets(nack_seq_num, timestamp)
                        entity.check_rlc_retx(nack_seq_num, timestamp)
