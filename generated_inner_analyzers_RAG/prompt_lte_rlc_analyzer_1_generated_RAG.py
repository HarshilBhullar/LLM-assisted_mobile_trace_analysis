
#!/usr/bin/python
# Filename: modified_lte_rlc_analyzer.py
"""
modified_lte_rlc_analyzer.py
A modified analyzer to provide detailed RLC layer information with adjusted metrics.
"""

__all__ = ["ModifiedLteRlcAnalyzer"]

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from mobile_insight.analyzer.analyzer import *

class ModifiedLteRlcAnalyzer(Analyzer):
    """
    An analyzer to provide detailed RLC layer information with modified metrics
    """
    def __init__(self):
        Analyzer.__init__(self)

        self.add_source_callback(self.__msg_callback)

        # Buffers and counters
        self.ul_sn_buffer = {}
        self.dl_sn_buffer = {}
        self.ul_cum_data = 0
        self.dl_cum_data = 0

    def set_source(self, source):
        """
        Set the trace source. Enable the specific logs for RLC layer.

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)

        # Enable RLC logs
        source.enable_log("LTE_RLC_UL_Config_Log_Packet")
        source.enable_log("LTE_RLC_DL_Config_Log_Packet")
        source.enable_log("LTE_RLC_UL_AM_All_PDU")
        source.enable_log("LTE_RLC_DL_AM_All_PDU")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_RLC_UL_Config_Log_Packet":
            log_item = msg.data.decode()
            # Process UL RLC configuration and broadcast changes
            for cfg in log_item.get('Subpackets', []):
                self.broadcast_info("RLC_UL_Config_Change", cfg)

        elif msg.type_id == "LTE_RLC_DL_Config_Log_Packet":
            log_item = msg.data.decode()
            # Process DL RLC configuration and broadcast changes
            for cfg in log_item.get('Subpackets', []):
                self.broadcast_info("RLC_DL_Config_Change", cfg)

        elif msg.type_id == "LTE_RLC_UL_AM_All_PDU":
            log_item = msg.data.decode()
            # Calculate UL throughput and frame costs
            for pdu in log_item.get('Subpackets', []):
                for am_pdu in pdu.get('PDUs', []):
                    sn = am_pdu['SN']
                    bytes_pdu = am_pdu['PDU Size']
                    self.ul_sn_buffer[sn] = bytes_pdu
                    self.ul_cum_data += bytes_pdu
                    self.log_info(f"UL Throughput: SN={sn}, Bytes={bytes_pdu}")
                    self.broadcast_info("RLC_UL_Throughput", {"SN": sn, "Bytes": bytes_pdu})

        elif msg.type_id == "LTE_RLC_DL_AM_All_PDU":
            log_item = msg.data.decode()
            # Calculate DL throughput and frame costs
            for pdu in log_item.get('Subpackets', []):
                for am_pdu in pdu.get('PDUs', []):
                    sn = am_pdu['SN']
                    bytes_pdu = am_pdu['PDU Size']
                    self.dl_sn_buffer[sn] = bytes_pdu
                    self.dl_cum_data += bytes_pdu
                    self.log_info(f"DL Throughput: SN={sn}, Bytes={bytes_pdu}")
                    self.broadcast_info("RLC_DL_Throughput", {"SN": sn, "Bytes": bytes_pdu})

    def get_ul_cumulative_data(self):
        """
        Get cumulative uplink data statistics

        :returns: cumulative uplink data
        :rtype: int
        """
        return self.ul_cum_data

    def get_dl_cumulative_data(self):
        """
        Get cumulative downlink data statistics

        :returns: cumulative downlink data
        :rtype: int
        """
        return self.dl_cum_data
