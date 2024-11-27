
from mobile_insight.analyzer.analyzer import Analyzer

class LteRlcAnalyzerModified(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.rb_info = {}

    def set_source(self, source):
        super().set_source(source)
        source.enable_log("LTE_RLC_UL_Config_Log_Packet")
        source.enable_log("LTE_RLC_DL_Config_Log_Packet")
        source.enable_log("LTE_RLC_UL_AM_All_PDU")
        source.enable_log("LTE_RLC_DL_AM_All_PDU")
        self.add_source_callback(self.__msg_callback)

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_RLC_UL_Config_Log_Packet" or msg.type_id == "LTE_RLC_DL_Config_Log_Packet":
            # Process configuration messages to update RB info
            decoded_msg = msg.decode()
            if 'Released RBs' in decoded_msg:
                for rb in decoded_msg['Released RBs']:
                    if rb in self.rb_info:
                        del self.rb_info[rb]
            if 'Active RBs' in decoded_msg:
                for rb in decoded_msg['Active RBs']:
                    self.rb_info[rb] = {'UL': 0, 'DL': 0}
            self.broadcast_info('RLC Config', self.rb_info)
            self.log_info("Active RBs: {}".format(len(self.rb_info)))

        elif msg.type_id == "LTE_RLC_UL_AM_All_PDU":
            # Process uplink PDUs
            decoded_msg = msg.decode()
            for rb in decoded_msg['RBs']:
                if rb in self.rb_info:
                    ul_data = sum(pdu['size'] for pdu in decoded_msg['RBs'][rb]['PDUs'])
                    self.rb_info[rb]['UL'] += ul_data * 1.1  # Increase by 10%
            self.broadcast_info('RLC UL Data', self.rb_info)

        elif msg.type_id == "LTE_RLC_DL_AM_All_PDU":
            # Process downlink PDUs
            decoded_msg = msg.decode()
            for rb in decoded_msg['RBs']:
                if rb in self.rb_info:
                    dl_data = sum(pdu['size'] for pdu in decoded_msg['RBs'][rb]['PDUs'])
                    self.rb_info[rb]['DL'] += dl_data * 0.9  # Decrease by 10%
            self.broadcast_info('RLC DL Data', self.rb_info)
