
#!/usr/bin/python
# Filename: lte_measurement_analyzer_mod.py
"""
lte_measurement_analyzer_mod.py
An analyzer to process LTE radio measurements

Author: Assistant
"""

from mobile_insight.analyzer.analyzer import *

__all__ = ["LteMeasurementAnalyzerMod"]

class LteMeasurementAnalyzerMod(Analyzer):
    """
    An analyzer to process and analyze LTE radio measurements
    """
    def __init__(self):
        Analyzer.__init__(self)

        self.add_source_callback(self.ue_event_filter)
        
        self.rsrp_list = []  # List to store RSRP measurements
        self.rsrq_list = []  # List to store RSRQ measurements
        self.avg_rsrp = None  # Variable to store average RSRP

    def set_source(self, source):
        """
        Set the trace source. Enable the necessary LTE PHY measurement logs

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)

        source.enable_log("LTE_PHY_Connected_Mode_Intra_Freq_Meas")
        source.enable_log("LTE_PHY_Serv_Cell_Measurement")
        source.enable_log("LTE_PHY_Neighbor_Cell_Measurement")
        source.enable_log("LTE_PHY_Inter_RAT_Measurement")

    def ue_event_filter(self, msg):
        """
        Callback function to process LTE measurement messages

        :param msg: incoming message
        """
        if msg.type_id == "LTE_PHY_Connected_Mode_Intra_Freq_Meas":
            log_item = msg.data.decode()
            if 'Records' in log_item:
                for record in log_item['Records']:
                    if 'Serving Cell' in record:
                        rsrp = record['Serving Cell']['RSRP']
                        rsrq = record['Serving Cell']['RSRQ']
                        self.rsrp_list.append(rsrp)
                        self.rsrq_list.append(rsrq)
                        self.log_info("RSRP: {}, RSRQ: {}".format(rsrp, rsrq))

                num_neighbors = len(log_item['Records']) - 1  # Exclude serving cell
                self.log_info("Number of Neighbor Cells: {}".format(num_neighbors))

                if self.rsrp_list:
                    self.avg_rsrp = sum(self.rsrp_list) / len(self.rsrp_list)
                    self.log_info("Average RSRP: {}".format(self.avg_rsrp))

    def get_rsrp_list(self):
        """
        Returns the list of RSRP measurements for the serving cell
        """
        return self.rsrp_list

    def get_rsrq_list(self):
        """
        Returns the list of RSRQ measurements for the serving cell
        """
        return self.rsrq_list

    def get_avg_rsrp(self):
        """
        Returns the average RSRP value calculated from the measurements
        """
        return self.avg_rsrp
