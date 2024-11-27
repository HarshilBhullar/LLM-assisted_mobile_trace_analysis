
#!/usr/bin/python
# Filename: modified_lte_rlc_analyzer.py
"""
A modified analyzer for LTE RLC layer with adjusted metrics.

Author: [Your Name]
"""

from .analyzer import *

class ModifiedLteRlcAnalyzer(Analyzer):
    """
    A modified analyzer for LTE RLC layer with adjusted metrics.
    """

    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)

        self.ul_sn_buffer = {}
        self.dl_sn_buffer = {}
        self.ul_ack_data = {}
        self.dl_ack_data = {}
        self.cumulative_ul_data = 0
        self.cumulative_dl_data = 0

    def set_source(self, source):
        """
        Set the source of the trace. Enable LTE RLC relevant logs.

        :param source: the source trace collector
        :type source: trace collector
        """
        Analyzer.set_source(self, source)
        source.enable_log("LTE_RLC_UL_Config_Log_Packet")
        source.enable_log("LTE_RLC_DL_Config_Log_Packet")
        source.enable_log("LTE_RLC_UL_AM_All_PDU")
        source.enable_log("LTE_RLC_DL_AM_All_PDU")

    def __msg_callback(self, msg):
        """
        Handle incoming messages related to RLC layer

        :param msg: the message object
        """
        if msg.type_id == "LTE_RLC_UL_Config_Log_Packet":
            self.__handle_ul_config(msg)
        elif msg.type_id == "LTE_RLC_DL_Config_Log_Packet":
            self.__handle_dl_config(msg)
        elif msg.type_id == "LTE_RLC_UL_AM_All_PDU":
            self.__handle_ul_am_pdu(msg)
        elif msg.type_id == "LTE_RLC_DL_AM_All_PDU":
            self.__handle_dl_am_pdu(msg)

    def __handle_ul_config(self, msg):
        """
        Handle uplink RLC configuration packets.

        :param msg: the message object
        """
        log_item = msg.data.decode()
        # Process configuration changes if necessary
        self.broadcast_info("UL_Config_Change", log_item)

    def __handle_dl_config(self, msg):
        """
        Handle downlink RLC configuration packets.

        :param msg: the message object
        """
        log_item = msg.data.decode()
        # Process configuration changes if necessary
        self.broadcast_info("DL_Config_Change", log_item)

    def __handle_ul_am_pdu(self, msg):
        """
        Handle uplink AM PDUs and calculate metrics.

        :param msg: the message object
        """
        log_item = msg.data.decode()
        for pdu in log_item.get('PDUs', []):
            sn = pdu.get('SN')
            pdu_size = pdu.get('PDU Size')
            self.cumulative_ul_data += pdu_size
            if sn not in self.ul_sn_buffer:
                self.ul_sn_buffer[sn] = pdu_size
            self.broadcast_info("UL_Throughput", {
                "timestamp": str(log_item["timestamp"]),
                "sn": sn,
                "pdu_size": pdu_size,
                "cumulative_data": self.cumulative_ul_data
            })

    def __handle_dl_am_pdu(self, msg):
        """
        Handle downlink AM PDUs and calculate metrics.

        :param msg: the message object
        """
        log_item = msg.data.decode()
        for pdu in log_item.get('PDUs', []):
            sn = pdu.get('SN')
            pdu_size = pdu.get('PDU Size')
            self.cumulative_dl_data += pdu_size
            if sn not in self.dl_sn_buffer:
                self.dl_sn_buffer[sn] = pdu_size
            self.broadcast_info("DL_Throughput", {
                "timestamp": str(log_item["timestamp"]),
                "sn": sn,
                "pdu_size": pdu_size,
                "cumulative_data": self.cumulative_dl_data
            })
