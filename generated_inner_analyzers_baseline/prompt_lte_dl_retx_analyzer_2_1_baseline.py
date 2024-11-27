
from mobile_insight.analyzer import Analyzer

class LteDlRetxAnalyzerModified(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.bearer_entity = {}
    
    def set_source(self, source):
        super().set_source(source)
        source.enable_log("LTE_RLC_UL_AM_All_PDU")
        source.enable_log("LTE_RLC_DL_AM_All_PDU")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_RLC_UL_AM_All_PDU":
            self.__msg_rlc_ul_callback(msg)
        elif msg.type_id == "LTE_RLC_DL_AM_All_PDU":
            self.__msg_rlc_dl_callback(msg)

    def __msg_rlc_ul_callback(self, msg):
        # Decode uplink RLC PDUs and process control PDUs for NACKs
        log_item = msg.data.decode()

        for pdu in log_item['Subpackets']:
            rb_id = pdu['RBID']
            if rb_id not in self.bearer_entity:
                self.bearer_entity[rb_id] = self.RadioBearerEntityModified(rb_id)

            self.bearer_entity[rb_id].process_ul_rlc_pdu(pdu)

    def __msg_rlc_dl_callback(self, msg):
        # Decode downlink RLC PDUs and process data PDUs for retransmissions
        log_item = msg.data.decode()

        for pdu in log_item['Subpackets']:
            rb_id = pdu['RBID']
            if rb_id not in self.bearer_entity:
                self.bearer_entity[rb_id] = self.RadioBearerEntityModified(rb_id)

            self.bearer_entity[rb_id].process_dl_rlc_pdu(pdu)
    
    class RadioBearerEntityModified:
        def __init__(self, rb_id):
            self.rb_id = rb_id
            self.mac_retx = []
            self.rlc_retx = []
            self.received_pdus = []

        def process_ul_rlc_pdu(self, pdu):
            # Process uplink RLC PDUs
            control_pdus = pdu.get('Control PDUs', [])
            for control_pdu in control_pdus:
                # Process NACKs
                pass

        def process_dl_rlc_pdu(self, pdu):
            # Process downlink RLC PDUs
            # Add logic to calculate retransmission delays
            data_pdus = pdu.get('Data PDUs', [])
            for data_pdu in data_pdus:
                self.received_pdus.append(data_pdu)
                # Calculate delay and append to the list
                delay = self.calculate_delay(data_pdu)
                if delay:
                    self.rlc_retx.append({'rlc_retx': delay})

        def calculate_delay(self, data_pdu):
            # Implement logic to calculate retransmission delay
            return 0.0  # Placeholder, replace with actual delay calculation logic
