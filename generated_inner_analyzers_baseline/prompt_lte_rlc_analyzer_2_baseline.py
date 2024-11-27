
from mobile_insight.analyzer import Analyzer

class ModifiedLteRlcAnalyzer(Analyzer):
    def __init__(self):
        super(ModifiedLteRlcAnalyzer, self).__init__()
        self.rbInfo = {}  # Dictionary to maintain RB state information

    def set_source(self, source):
        """
        Configure logs to enable for analysis.
        """
        source.enable_log("LTE_RLC_UL_Config_Log_Packet")
        source.enable_log("LTE_RLC_DL_Config_Log_Packet")
        source.enable_log("LTE_RLC_UL_AM_All_PDU")
        source.enable_log("LTE_RLC_DL_AM_All_PDU")
        super(ModifiedLteRlcAnalyzer, self).set_source(source)

    def __msg_callback(self, msg):
        """
        Handle message callbacks for the configured logs.
        """
        if msg.type_id == "LTE_RLC_UL_Config_Log_Packet" or msg.type_id == "LTE_RLC_DL_Config_Log_Packet":
            self._process_rlc_config(msg)
        
        elif msg.type_id == "LTE_RLC_UL_AM_All_PDU" or msg.type_id == "LTE_RLC_DL_AM_All_PDU":
            self._process_rlc_pdu(msg)

    def _process_rlc_config(self, msg):
        """
        Process RLC configuration messages to track active and released RBs.
        """
        # Extract RB configuration and update self.rbInfo
        log_item = msg.data.decode()
        for rb in log_item.get("Subpackets", []):
            rb_id = rb.get("rb_cfg_idx", None)
            if rb_id is not None:
                # Initialize or update rbInfo with configuration state
                self.rbInfo[rb_id] = self.rbInfo.get(rb_id, {})
                self.rbInfo[rb_id]['active'] = rb.get("RLC mode", "Unknown")

    def _process_rlc_pdu(self, msg):
        """
        Process RLC PDU messages to calculate cumulative data and throughput.
        """
        log_item = msg.data.decode()
        for pdu in log_item.get("Subpackets", []):
            rb_id = pdu.get("rb_cfg_idx", None)
            if rb_id is not None:
                pdu_bytes = pdu.get("PDU SIZE", 0)
                cumulative_data = self.rbInfo[rb_id].get("cumulative_data", 0) + pdu_bytes
                self.rbInfo[rb_id]["cumulative_data"] = cumulative_data
                
                # Calculate throughput with adjusted factor
                throughput = (pdu_bytes * 1.1) / (log_item.get("timestamp", 1))
                self.rbInfo[rb_id]["throughput"] = throughput

                # Log throughput information
                self.log_info("RB Config ID: {}, Timestamp: {}, Throughput: {:.2f} bytes/s".format(
                    rb_id, log_item.get("timestamp", ""), throughput))

    def set_source(self, source):
        """
        Configure the source for the analyzer.
        """
        super(ModifiedLteRlcAnalyzer, self).set_source(source)
        source.set_callback(self.__msg_callback)
