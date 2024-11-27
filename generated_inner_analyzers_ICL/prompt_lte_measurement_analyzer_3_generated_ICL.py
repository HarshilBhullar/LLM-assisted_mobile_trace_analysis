
#!/usr/bin/python
# Filename: lte_measurement_analyzer_modified.py
"""
lte_measurement_analyzer_modified.py
A modified analyzer for processing LTE radio measurements

Author: Yuanjie Li
"""

__all__ = ["LteMeasurementAnalyzerModified"]

from ..analyzer import Analyzer
import xml.etree.ElementTree as ET

class LteMeasurementAnalyzerModified(Analyzer):

    """
    An analyzer for processing LTE radio measurements
    """

    def __init__(self):
        Analyzer.__init__(self)
        self.rsrp_list = []
        self.rsrq_list = []
        self.avg_neighbor_rsrp_list = []
        self.add_source_callback(self.ue_event_filter)

    def set_source(self, source):
        """
        Set the trace source. Enable the LTE measurement logs.

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)
        source.enable_log("LTE_PHY_Connected_Mode_Intra_Freq_Meas")
        source.enable_log("LTE_PHY_Serv_Cell_Measurement")
        source.enable_log("LTE_PHY_Connected_Mode_Neighbor_Measurement")
        source.enable_log("LTE_PHY_Inter_RAT_Measurement")
        source.enable_log("LTE_PHY_Inter_RAT_CDMA_Measurement")

    def ue_event_filter(self, msg):
        """
        Filter LTE measurement messages and process them

        :param msg: the event (message) from the trace collector.
        """
        if msg.type_id == "LTE_PHY_Connected_Mode_Intra_Freq_Meas":
            self.log_info("Processing LTE_PHY_Connected_Mode_Intra_Freq_Meas")

            log_item = msg.data.decode()
            log_item_dict = dict(log_item)

            if 'Serving Cell' in log_item_dict:
                serving_cell = log_item_dict['Serving Cell']
                rsrp = float(serving_cell['RSRP'])
                rsrq = float(serving_cell['RSRQ'])
                self.rsrp_list.append(rsrp)
                self.rsrq_list.append(rsrq)
                self.log_info(f"Serving Cell - RSRP: {rsrp}, RSRQ: {rsrq}, Timestamp: {msg.timestamp}")

            if 'Neighbor Cells' in log_item_dict:
                neighbor_cells = log_item_dict['Neighbor Cells']
                total_rsrp = 0
                num_neighbors = 0
                for neighbor in neighbor_cells:
                    if 'RSRP' in neighbor:
                        total_rsrp += float(neighbor['RSRP'])
                        num_neighbors += 1
                if num_neighbors > 0:
                    avg_rsrp = total_rsrp / num_neighbors
                    self.avg_neighbor_rsrp_list.append(avg_rsrp)
                    self.log_info(f"Average Neighbor RSRP: {avg_rsrp}, Timestamp: {msg.timestamp}")

    def get_rsrp_list(self):
        """
        Returns a list of RSRP measurements for the serving cell
        """
        return self.rsrp_list

    def get_rsrq_list(self):
        """
        Returns a list of RSRQ measurements for the serving cell
        """
        return self.rsrq_list

    def get_avg_neighbor_rsrp_list(self):
        """
        Returns a list of average RSRP values for neighbor cells
        """
        return self.avg_neighbor_rsrp_list
