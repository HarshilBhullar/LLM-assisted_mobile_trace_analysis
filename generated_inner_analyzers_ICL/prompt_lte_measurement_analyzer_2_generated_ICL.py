
#!/usr/bin/python
# Filename: modified_lte_measurement_analyzer.py
"""
A modified LTE Measurement analyzer for additional metrics.
"""

from mobile_insight.analyzer.analyzer import *

__all__ = ["ModifiedLteMeasurementAnalyzer"]

class ModifiedLteMeasurementAnalyzer(Analyzer):
    """
    A modified analyzer to provide additional metrics for LTE radio measurements.
    """

    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__ue_event_filter)

        self.rsrp_list = []
        self.rsrq_list = []
        self.rssi_list = []

    def set_source(self, source):
        """
        Set the trace source. Enable the LTE internal logs.

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)

        source.enable_log("LTE_PHY_Connected_Mode_Intra-Freq_Meas")
        source.enable_log("LTE_PHY_Serv_Cell_Measurement")
        source.enable_log("LTE_PHY_Connected_Mode_Neighbor_Meas")
        source.enable_log("LTE_PHY_Inter_RAT_Measurement")

    def __ue_event_filter(self, msg):
        """
        Filter all LTE measurement packets, and process the serving cell RSRP messages.

        :param msg: the event (message) from the trace collector.
        """
        if msg.type_id == "LTE_PHY_Serv_Cell_Measurement":
            log_item = msg.data.decode()
            if 'Serving Cell' in log_item:
                for serv_cell in log_item['Serving Cell']:
                    timestamp = log_item['timestamp']
                    rsrp = serv_cell.get('RSRP', None)
                    rsrq = serv_cell.get('RSRQ', None)
                    rssi = rsrp - 141 if rsrp is not None else None  # Convert RSRP to RSSI

                    if rsrp is not None:
                        self.rsrp_list.append((timestamp, rsrp))
                    if rsrq is not None:
                        self.rsrq_list.append((timestamp, rsrq))
                    if rssi is not None:
                        self.rssi_list.append((timestamp, rssi))

                    self.log_info("Timestamp: {}, RSRP: {}, RSRQ: {}, RSSI: {}".format(timestamp, rsrp, rsrq, rssi))

    def get_rsrp_list(self):
        """
        Get the list of RSRP measurements.

        :return: RSRP list
        """
        return self.rsrp_list

    def get_rsrq_list(self):
        """
        Get the list of RSRQ measurements.

        :return: RSRQ list
        """
        return self.rsrq_list

    def get_rssi_list(self):
        """
        Get the list of RSSI measurements.

        :return: RSSI list
        """
        return self.rssi_list
