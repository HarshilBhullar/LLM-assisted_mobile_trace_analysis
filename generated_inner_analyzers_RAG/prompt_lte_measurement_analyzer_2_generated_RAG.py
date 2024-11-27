
#!/usr/bin/python
# Filename: modified_lte_measurement_analyzer.py
"""
modified_lte_measurement_analyzer.py
A modified analyzer to provide additional metrics for LTE radio measurements.
"""

__all__ = ["ModifiedLteMeasurementAnalyzer"]

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from mobile_insight.analyzer.analyzer import *

class ModifiedLteMeasurementAnalyzer(Analyzer):
    """
    A modified analyzer to monitor LTE radio measurements with additional metrics
    """
    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)

        # Initialize lists to store measurements
        self.rsrp_list = []
        self.rsrq_list = []
        self.rssi_list = []

    def set_source(self, source):
        """
        Set the trace source. Enable the LTE internal logs.

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)

        source.enable_log("LTE_PHY_Connected_Mode_Intra_Freq_Meas")
        source.enable_log("LTE_PHY_Serving_Cell_Measurement")
        source.enable_log("LTE_PHY_Connected_Mode_Neighbor_Meas")
        source.enable_log("LTE_PHY_Inter_RAT_Measurement")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_PHY_Serving_Cell_Measurement":
            log_item = msg.data.decode()
            if 'Records' in log_item:
                for record in log_item['Records']:
                    if 'RSRP' in record:
                        self.rsrp_list.append((log_item['timestamp'], record['RSRP']))
                    if 'RSRQ' in record:
                        self.rsrq_list.append((log_item['timestamp'], record['RSRQ']))
                    if 'RSSI' in record:
                        self.rssi_list.append((log_item['timestamp'], record['RSSI']))

    def get_rsrp_list(self):
        """
        Retrieve the list of RSRP measurements.

        :return: List of RSRP measurements with timestamps.
        """
        return self.rsrp_list

    def get_rsrq_list(self):
        """
        Retrieve the list of RSRQ measurements.

        :return: List of RSRQ measurements with timestamps.
        """
        return self.rsrq_list

    def get_rssi_list(self):
        """
        Retrieve the list of RSSI measurements.

        :return: List of RSSI measurements with timestamps.
        """
        return self.rssi_list
