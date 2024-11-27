
from mobile_insight.analyzer.analyzer import *

class ModifiedLteRlcAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.set_source(None)

        self.ul_sn_buffer = {}
        self.dl_sn_buffer = {}
        self.ul_ack_buffer = {}
        self.dl_ack_buffer = {}
        self.ul_data_counter = 0
        self.dl_data_counter = 0
        self.ul_throughput = 0
        self.dl_throughput = 0

    def set_source(self, source):
        """
        Set the trace source. Enable the required log types.
        """
        Analyzer.set_source(self, source)
        source.enable_log("LTE_RLC_UL_Config_Log_Packet")
        source.enable_log("LTE_RLC_DL_Config_Log_Packet")
        source.enable_log("LTE_RLC_UL_AM_All_PDU")
        source.enable_log("LTE_RLC_DL_AM_All_PDU")

    def __msg_callback(self, msg):
        """
        Callback function to handle incoming messages and calculate performance metrics.
        """
        if msg.type_id == "LTE_RLC_UL_Config_Log_Packet":
            # Handle uplink config changes
            self.__process_ul_config(msg)

        elif msg.type_id == "LTE_RLC_DL_Config_Log_Packet":
            # Handle downlink config changes
            self.__process_dl_config(msg)

        elif msg.type_id == "LTE_RLC_UL_AM_All_PDU":
            # Calculate uplink throughput and frame costs
            self.__process_ul_pdu(msg)

        elif msg.type_id == "LTE_RLC_DL_AM_All_PDU":
            # Calculate downlink throughput and frame costs
            self.__process_dl_pdu(msg)

    def __process_ul_config(self, msg):
        # Handle uplink configuration
        # Placeholder for configuration logic
        self.log_info("UL Config: {}".format(msg))

    def __process_dl_config(self, msg):
        # Handle downlink configuration
        # Placeholder for configuration logic
        self.log_info("DL Config: {}".format(msg))

    def __process_ul_pdu(self, msg):
        # Process uplink PDUs and calculate throughput
        pdu_bytes = self.__get_pdu_bytes(msg)
        self.ul_data_counter += pdu_bytes
        self.ul_throughput = self.__calculate_throughput(self.ul_data_counter)
        self.log_info("UL Throughput: {} bytes/s".format(self.ul_throughput))

    def __process_dl_pdu(self, msg):
        # Process downlink PDUs and calculate throughput
        pdu_bytes = self.__get_pdu_bytes(msg)
        self.dl_data_counter += pdu_bytes
        self.dl_throughput = self.__calculate_throughput(self.dl_data_counter)
        self.log_info("DL Throughput: {} bytes/s".format(self.dl_throughput))

    def __get_pdu_bytes(self, msg):
        # Extract the byte size of the PDU from the message
        # Placeholder for actual byte extraction logic
        return len(msg.data)

    def __calculate_throughput(self, data_counter):
        # Calculate throughput based on cumulative data
        # Placeholder for actual throughput calculation
        return data_counter
