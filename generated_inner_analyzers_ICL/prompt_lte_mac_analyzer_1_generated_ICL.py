
#!/usr/bin/python
# Filename: lte_mac_analyzer_modified.py
"""
lte_mac_analyzer_modified.py
A modified analyzer for 4G MAC-layer metrics with additional evaluations

Author: [Your Name]
"""

from .analyzer import *

__all__ = ["LteMacAnalyzerModified"]

class LteMacAnalyzerModified(Analyzer):
    """
    A modified analyzer for LTE MAC-layer metrics with additional evaluations
    """
    def __init__(self):
        Analyzer.__init__(self)

        self.add_source_callback(self.__msg_callback)

        self.ul_grant_utilization = []
        self.buffer_status = {}
        self.harq_failures = 0
        self.retransmissions = 0

    def set_source(self, source):
        """
        Set the trace source. Enable necessary logs for MAC layer analysis

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)
        source.enable_log("LTE_MAC_UL_Tx_Statistics")
        source.enable_log("LTE_MAC_UL_Buffer_Status_Internal")
        source.enable_log("LTE_PHY_PDSCH_Stat_Indication")

    def __msg_callback(self, msg):
        """
        Callback function to handle incoming messages and perform analysis

        :param msg: the message object
        """
        if msg.type_id == "LTE_MAC_UL_Tx_Statistics":
            self.__process_ul_tx_statistics(msg)
        elif msg.type_id == "LTE_MAC_UL_Buffer_Status_Internal":
            self.__process_buffer_status(msg)
        elif msg.type_id == "LTE_PHY_PDSCH_Stat_Indication":
            self.__process_pdsch_stat(msg)

    def __process_ul_tx_statistics(self, msg):
        """
        Process UL Tx Statistics to compute utilization and variance

        :param msg: the message object containing UL Tx stats
        """
        log_item = msg.data.decode()
        if 'Subpackets' in log_item:
            for subpkt in log_item['Subpackets']:
                ul_grant = subpkt.get('UL Grant', 0)
                ul_data = subpkt.get('UL Data', 0)
                if ul_grant > 0:
                    utilization = ul_data / ul_grant
                    self.ul_grant_utilization.append(utilization)

                    bcast_dict = {
                        'timestamp': str(log_item['timestamp']),
                        'ul_grant_utilization': str(utilization)
                    }
                    self.broadcast_info("UL_GRANT_UTILIZATION", bcast_dict)

    def __process_buffer_status(self, msg):
        """
        Process buffer status to analyze delays and manage buffer

        :param msg: the message object containing buffer status
        """
        log_item = msg.data.decode()
        if 'Subpackets' in log_item:
            for subpkt in log_item['Subpackets']:
                buffer_size = subpkt.get('Buffer Size', 0)
                lcid = subpkt.get('LCID', None)
                if lcid is not None:
                    self.buffer_status[lcid] = buffer_size

                    bcast_dict = {
                        'timestamp': str(log_item['timestamp']),
                        'lcid': str(lcid),
                        'buffer_size': str(buffer_size)
                    }
                    self.broadcast_info("BUFFER_STATUS", bcast_dict)

    def __process_pdsch_stat(self, msg):
        """
        Process PDSCH statistics to track HARQ failures and retransmissions

        :param msg: the message object containing PDSCH stats
        """
        log_item = msg.data.decode()
        if 'Subpackets' in log_item:
            for subpkt in log_item['Subpackets']:
                harq_failure = subpkt.get('HARQ Failure', 0)
                retransmission = subpkt.get('Retransmission', 0)

                self.harq_failures += harq_failure
                self.retransmissions += retransmission

                bcast_dict = {
                    'timestamp': str(log_item['timestamp']),
                    'harq_failures': str(self.harq_failures),
                    'retransmissions': str(self.retransmissions)
                }
                self.broadcast_info("MAC_LAYER_RETRANSMISSIONS", bcast_dict)

