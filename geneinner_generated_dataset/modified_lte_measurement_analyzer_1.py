
#!/usr/bin/python
# Filename: lte_measurement_analyzer_modified.py
"""
An modified analyzer for LTE radio measurements

Author: Yuanjie Li
"""

from .analyzer import *

import datetime


class LteMeasurementAnalyzerModified(Analyzer):
    """
    A modified analyzer for LTE radio measurements
    """

    def __init__(self):

        Analyzer.__init__(self)

        # init packet filters
        self.add_source_callback(self.ue_event_filter)

        self.serv_cell_rsrp = []  # rsrp measurements
        self.serv_cell_rsrq = []  # rsrq measurements
        self.serv_cell_rssi = []  # new metric: rssi measurements

    def set_source(self, source):
        """
        Set the source of the trace.
        Enable device's LTE internal logs.

        :param source: the source trace collector
        :param type: trace collector
        """
        Analyzer.set_source(self, source)
        # enable user's internal events
        source.enable_log("LTE_PHY_Connected_Mode_Intra_Freq_Meas")
        source.enable_log("LTE_PHY_Serv_Cell_Measurement")
        source.enable_log("LTE_PHY_Connected_Mode_Neighbor_Measurement")
        source.enable_log("LTE_PHY_Inter_RAT_Measurement")
        source.enable_log("LTE_PHY_Inter_RAT_CDMA_Measurement")

    def ue_event_filter(self, msg):
        """
        callback to handle user events

        :param source: the source trace collector
        :param type: trace collector
        """
        # TODO: support more user events
        self.serving_cell_rsrp(msg)

    def serving_cell_rsrp(self, msg):
        if msg.type_id == "LTE_PHY_Connected_Mode_Intra_Freq_Meas":

            msg_dict = dict(msg.data.decode())
            date = msg_dict['timestamp'].strftime('%Y-%m-%d %H:%M:%S.%f')
            # New RSSI calculation or retrieval
            rssi_value = self.calculate_rssi(msg_dict['RSRP(dBm)'], msg_dict['RSRQ(dB)'])
            rsrp_log = (str(date) +
                        ":" +
                        self.__class__.__name__ +
                        ' RSRP=' +
                        str(msg_dict['RSRP(dBm)']) +
                        'dBm' +
                        ' RSRQ=' +
                        str(msg_dict['RSRQ(dB)']) +
                        'dB' +
                        ' RSSI=' +
                        str(rssi_value) +
                        'dBm' +
                        ' # of neighbors=' +
                        str(msg_dict['Number of Neighbor Cells']) +
                        '\n')

            for item in msg_dict["Neighbor Cells"]:
                rsrp_log = (rsrp_log
                            + '    Cell_ID=' + str(item["Physical Cell ID"])
                            + ' RSRP=' + str(item["RSRP(dBm)"]) + 'dBm'
                            + ' RSRQ=' + str(item["RSRQ(dB)"]) + 'dB'
                            + '\n')

            self.log_info(rsrp_log)

            self.serv_cell_rsrp.append(msg_dict['RSRP(dBm)'])
            self.serv_cell_rsrq.append(msg_dict['RSRQ(dB)'])
            self.serv_cell_rssi.append(rssi_value)

    def calculate_rssi(self, rsrp, rsrq):
        """
        Calculate RSSI based on RSRP and RSRQ.

        :param rsrp: Reference Signal Received Power
        :param rsrq: Reference Signal Received Quality
        :return: Calculated RSSI
        """
        # Simplistic RSSI calculation for demonstration purposes
        rssi = rsrp + rsrq  # Adjust this formula based on actual calculation needs
        return rssi

    def get_rsrp_list(self):
        """
        Get serving cell's RSRP measurement

        :returns: a list of serving cell's measurement
        :rtype: list
        """
        return self.serv_cell_rsrp

    def get_rsrq_list(self):
        """
        Get serving cell's RSRQ measurement

        :returns: a list of serving cell's measurement
        :rtype: list
        """
        return self.serv_cell_rsrq
        
    def get_rssi_list(self):
        """
        Get serving cell's RSSI measurement

        :returns: a list of serving cell's measurement
        :rtype: list
        """
        return self.serv_cell_rssi
