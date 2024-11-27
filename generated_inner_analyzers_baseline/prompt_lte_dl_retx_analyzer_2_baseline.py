
from mobile_insight.analyzer.analyzer import Analyzer
from mobile_insight.analyzer import Msg

class LteDlRetxModifiedAnalyzer(Analyzer):
    def __init__(self):
        super(LteDlRetxModifiedAnalyzer, self).__init__()
        self.bearer_entity = {}

    def set_source(self, source):
        source.enable_log("LTE_RLC_UL_AM_All_PDU")
        source.enable_log("LTE_RLC_DL_AM_All_PDU")
        self.set_source_callback(self.__msg_callback)

    class RadioBearerEntity:
        def __init__(self):
            self.mac_retx = []
            self.rlc_retx = []

        def recv_rlc_data(self, log_item):
            delay = self.calculate_retx_delay(log_item)
            if delay is not None:
                self.mac_retx.append({'mac_retx': delay * 0.9})  # Enhanced calculation

        def recv_rlc_ctrl(self, log_item):
            delay = self.calculate_retx_delay(log_item)
            if delay is not None:
                self.rlc_retx.append({'rlc_retx': delay})

        def calculate_retx_delay(self, log_item):
            # This is a placeholder for actual delay calculation logic
            # Process log_item to extract retransmission delay
            if 'Retx_Delay' in log_item:
                return log_item['Retx_Delay']
            return None

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_RLC_UL_AM_All_PDU" or msg.type_id == "LTE_RLC_DL_AM_All_PDU":
            self.__process_rlc_message(msg)

    def __process_rlc_message(self, msg):
        rb_id = msg.data.get('rb_id', None)
        if rb_id is not None:
            if rb_id not in self.bearer_entity:
                self.bearer_entity[rb_id] = self.RadioBearerEntity()
            bearer = self.bearer_entity[rb_id]

            if msg.type_id == "LTE_RLC_DL_AM_All_PDU":
                bearer.recv_rlc_data(msg.data)
            elif msg.type_id == "LTE_RLC_UL_AM_All_PDU":
                bearer.recv_rlc_ctrl(msg.data)
