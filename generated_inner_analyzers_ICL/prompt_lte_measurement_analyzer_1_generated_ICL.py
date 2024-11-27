
#!/usr/bin/python
# Filename: lte_measurement_analyzer_mod.py
"""
lte_measurement_analyzer_mod.py
An analyzer to monitor LTE radio measurements

Author: Assistant
"""

from mobile_insight.analyzer.analyzer import *

__all__ = ["LteMeasurementAnalyzerMod"]

class LteMeasurementAnalyzerMod(Analyzer):
    """
    An analyzer to monitor LTE radio measurements
    """
    def __init__(self):
        Analyzer.__init__(self)

        self.add_source_callback(self.ue_event_filter)
        self.rsrp_list = []
        self.rsrq_list = []
        self.avg_rsrp = None

    def set_source(self, source):
        """
        Set the trace source. Enable the cellular signaling messages

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)

        # Enable specific LTE PHY measurement logs
        source.enable_log("LTE_PHY_Connected_Mode_Intra_Freq_Meas")
        source.enable_log("LTE_PHY_Serv_Cell_Measurement")
        source.enable_log("LTE_PHY_Neighbor_Cell_Measurement")
        source.enable_log("LTE_PHY_Inter_RAT_Measurement")

    def ue_event_filter(self, msg):
        if msg.type_id == "LTE_PHY_Connected_Mode_Intra_Freq_Meas":
            log_item = msg.data.decode()
            
            if 'Subpackets' in log_item:
                for pkt in log_item['Subpackets']:
                    if 'Cells' in pkt:
                        for cell in pkt['Cells']:
                            if 'RSRP' in cell and 'RSRQ' in cell:
                                rsrp = float(cell['RSRP'])
                                rsrq = float(cell['RSRQ'])
                                self.rsrp_list.append(rsrp)
                                self.rsrq_list.append(rsrq)
                                self.log_info(f"RSRP: {rsrp}, RSRQ: {rsrq}")

                # Calculate average RSRP
                self.avg_rsrp = sum(self.rsrp_list) / len(self.rsrp_list)
                self.log_info(f"Average RSRP: {self.avg_rsrp}")

    def get_rsrp_list(self):
        return self.rsrp_list

    def get_rsrq_list(self):
        return self.rsrq_list

    def get_avg_rsrp(self):
        return self.avg_rsrp
