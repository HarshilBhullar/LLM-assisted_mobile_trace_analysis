
#!/usr/bin/python
# Filename: modified_lte_measurement_analyzer.py
"""
A modified analyzer for LTE radio measurements with additional metrics.

Author: Yuanjie Li
Modified by: [Your Name]
"""

from .analyzer import *

import datetime


class ModifiedLteMeasurementAnalyzer(Analyzer):
    """
    A modified analyzer for LTE radio measurements with additional metrics.
    """

    def __init__(self):

        Analyzer.__init__(self)

        # init packet filters
        self.add_source_callback(self.ue_event_filter)

        self.serv_cell_rsrp = []  # rsrp measurements
        self.serv_cell_rsrq = []  # rsrq measurements
        self.serv_cell_rssi = []  # additional rssi measurements

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
                        str(msg_dict.get('RSSI(dBm)', 'N/A')) +
                        'dBm' +
                        ' # of neighbors=' +
                        str(msg_dict['Number of Neighbor Cells']) +
                        '\n')

            for item in msg_dict["Neighbor Cells"]:
                rsrp_log = (rsrp_log
                            + '    Cell_ID=' + str(item["Physical Cell ID"])
                            + ' RSRP=' + str(item["RSRP(dBm)"]) + 'dBm'
                            + ' RSRQ=' + str(item["RSRQ(dB)"]) + 'dB'
                            + ' RSSI=' + str(item.get("RSSI(dBm)", 'N/A')) + 'dBm'
                            + '\n')

            self.log_info(rsrp_log)

            self.serv_cell_rsrp.append(msg_dict['RSRP(dBm)'])
            self.serv_cell_rsrq.append(msg_dict['RSRQ(dB)'])
            self.serv_cell_rssi.append(msg_dict.get('RSSI(dBm)', None))

        # if msg.type_id == "LTE_PHY_Inter_RAT_Measurement":
        #     msg_dict=dict(msg.data.decode())
        #     self.log_info(str(msg_dict))

        # if msg.type_id == "LTE_PHY_Inter_RAT_CDMA_Measurement":
        #     msg_dict=dict(msg.data.decode())
        #     self.log_info(str(msg_dict))

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
