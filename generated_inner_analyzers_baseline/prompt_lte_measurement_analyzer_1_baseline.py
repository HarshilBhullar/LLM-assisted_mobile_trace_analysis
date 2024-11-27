
from mobile_insight.analyzer import Analyzer

class LteMeasurementAnalyzerMod(Analyzer):
    def __init__(self):
        super(LteMeasurementAnalyzerMod, self).__init__()
        self.add_source_callback(self.ue_event_filter)
        
        self.rsrp_list = []
        self.rsrq_list = []
        self.avg_rsrp = 0.0

    def ue_event_filter(self, msg):
        # Check if the message is the desired LTE PHY measurement
        if msg.type_id == "LTE_PHY_Connected_Mode_Intra_Freq_Meas":
            # Extract relevant measurement data
            log_item = msg.data.decode()
            
            if 'NeighborCells' in log_item:
                for cell in log_item['NeighborCells']:
                    if 'RSRP' in cell:
                        self.rsrp_list.append(cell['RSRP'])
                    if 'RSRQ' in cell:
                        self.rsrq_list.append(cell['RSRQ'])

            # Calculate average RSRP
            if self.rsrp_list:
                self.avg_rsrp = sum(self.rsrp_list) / len(self.rsrp_list)

            # Log the measurements
            print(f"RSRP List: {self.rsrp_list}")
            print(f"RSRQ List: {self.rsrq_list}")
            print(f"Average RSRP: {self.avg_rsrp}")

    def get_rsrp_list(self):
        return self.rsrp_list

    def get_rsrq_list(self):
        return self.rsrq_list

    def get_avg_rsrp(self):
        return self.avg_rsrp
