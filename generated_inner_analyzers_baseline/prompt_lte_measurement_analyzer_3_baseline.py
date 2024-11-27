
from mobile_insight.analyzer.analyzer import Analyzer

class LteMeasurementAnalyzerModified(Analyzer):
    def __init__(self):
        super(LteMeasurementAnalyzerModified, self).__init__()
        self.rsrp_list = []
        self.rsrq_list = []
        self.avg_neighbor_rsrp_list = []

    def set_source(self, source):
        """
        Set the trace source. Enable the necessary LTE measurement messages.
        """
        source.enable_log("LTE_PHY_Connected_Mode_Intra_Freq_Meas")
        source.enable_log("LTE_PHY_Serv_Cell_Measurement")
        source.enable_log("LTE_PHY_Connected_Mode_Neighbor_Measurement")
        source.enable_log("LTE_PHY_Inter_RAT_Measurement")
        source.enable_log("LTE_PHY_Inter_RAT_CDMA_Measurement")
        super(LteMeasurementAnalyzerModified, self).set_source(source)

    def ue_event_filter(self, msg):
        """
        Filter and process LTE measurement messages.
        """
        if msg.type_id == "LTE_PHY_Connected_Mode_Intra_Freq_Meas":
            log_item = msg.data.decode()
            timestamp = msg.timestamp

            # Process the serving cell measurements
            if 'servingCell' in log_item:
                serving_cell = log_item['servingCell']
                if 'RSRP' in serving_cell:
                    rsrp = serving_cell['RSRP']
                    self.rsrp_list.append((timestamp, rsrp))
                if 'RSRQ' in serving_cell:
                    rsrq = serving_cell['RSRQ']
                    self.rsrq_list.append((timestamp, rsrq))

            # Process neighbor cell measurements
            if 'neighborCells' in log_item:
                neighbor_cells = log_item['neighborCells']
                for neighbor in neighbor_cells:
                    if 'RSRP' in neighbor:
                        neighbor_rsrp = neighbor['RSRP']
                        self.avg_neighbor_rsrp_list.append((timestamp, neighbor_rsrp))

    def get_rsrp_list(self):
        """
        Retrieve the list of RSRP measurements for the serving cell.
        """
        return self.rsrp_list

    def get_rsrq_list(self):
        """
        Retrieve the list of RSRQ measurements for the serving cell.
        """
        return self.rsrq_list

    def get_avg_neighbor_rsrp_list(self):
        """
        Retrieve the list of average RSRP values for neighbor cells.
        """
        return self.avg_neighbor_rsrp_list
