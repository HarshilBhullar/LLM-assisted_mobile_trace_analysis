
from mobileinsight.analyzer.analyzer import Analyzer
from mobileinsight.analyzer import MsgLogger
from datetime import datetime

class ModifiedLteMeasurementAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.rsrp_list = []
        self.rsrq_list = []
        self.rssi_list = []

    def set_source(self, source):
        Analyzer.set_source(self, source)
        self.source = source
        
        self.source.enable_log("LTE_PHY_Connected_Mode_Intra_Freq_Measurement")
        self.source.enable_log("LTE_PHY_Serv_Cell_Measurement")
        self.source.enable_log("LTE_PHY_Connected_Mode_Neighbor_Measurement")
        self.source.enable_log("LTE_RRC_Inter_RAT_Measurement_Indication")
        
        self.source.add_callback(self.ue_event_filter)

    def ue_event_filter(self, msg):
        if msg.type_id == "LTE_PHY_Serv_Cell_Measurement":
            decoded_msg = msg.data.decode()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if 'RSRP' in decoded_msg:
                rsrp = decoded_msg.get('RSRP', None)
                rsrq = decoded_msg.get('RSRQ', None)
                rssi = decoded_msg.get('RSSI', None)
                
                if rsrp is not None:
                    self.rsrp_list.append((timestamp, rsrp))
                if rsrq is not None:
                    self.rsrq_list.append((timestamp, rsrq))
                if rssi is not None:
                    self.rssi_list.append((timestamp, rssi))
                
                self.log_info("Serving Cell Measurement: Timestamp:{} RSRP:{} RSRQ:{} RSSI:{}".format(
                    timestamp, rsrp, rsrq, rssi))
                
                if 'Neighbor Cells' in decoded_msg:
                    neighbors = decoded_msg.get('Neighbor Cells', [])
                    for neighbor in neighbors:
                        self.log_info("Neighbor Cell: {}".format(neighbor))

    def get_rsrp_list(self):
        return self.rsrp_list

    def get_rsrq_list(self):
        return self.rsrq_list

    def get_rssi_list(self):
        return self.rssi_list
