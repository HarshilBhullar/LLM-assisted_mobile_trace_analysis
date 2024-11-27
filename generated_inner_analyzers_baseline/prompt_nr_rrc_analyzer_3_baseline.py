
from mobile_insight.analyzer import ProtocolAnalyzer

class NrRrcAnalyzerModified(ProtocolAnalyzer):
    def __init__(self):
        super(NrRrcAnalyzerModified, self).__init__()
        self.add_source_callback(self.__rrc_filter)
        self.cell_status = {}
        self.cell_history = []
        self.cell_configurations = {}

    def __rrc_filter(self, msg):
        if msg.type_id == "5G_NR_RRC_OTA_Packet":
            xml_msg = msg.data.decode("utf-8")
            # Parse the XML message
            freq = self.__extract_frequency(xml_msg)
            cell_id = self.__extract_cell_id(xml_msg)
            self.__update_conn(freq, cell_id)
            if "RRCConnectionSetup" in xml_msg:
                self.__callback_rrc_conn(xml_msg)
            elif "SystemInformationBlock" in xml_msg:
                self.__callback_sib_config(xml_msg)
            elif "RRCReconfiguration" in xml_msg:
                self.__callback_rrc_reconfig(xml_msg)
            self.log_info("Processed NR RRC message.")

    def __callback_sib_config(self, xml_msg):
        # Extract configurations from SIB
        sib_info = self.__parse_sib(xml_msg)
        self.cell_configurations[sib_info['cell_id']] = sib_info
        self.log_info(f"SIB Config: {sib_info}")

    def __callback_rrc_reconfig(self, xml_msg):
        # Extract configurations from RRCReconfiguration
        reconfig_info = self.__parse_rrc_reconfig(xml_msg)
        self.cell_configurations[reconfig_info['cell_id']] = reconfig_info
        self.log_info(f"RRC Reconfig: {reconfig_info}")

    def __callback_rrc_conn(self, xml_msg):
        # Update RRC connectivity status
        conn_status = self.__parse_rrc_connection(xml_msg)
        self.cell_status[conn_status['cell_id']] = conn_status
        self.log_info(f"RRC Connection: {conn_status}")

    def __update_conn(self, freq, cell_id):
        # Update current cell status
        self.cell_status[cell_id] = {'frequency': freq, 'cell_id': cell_id}
        if cell_id not in self.cell_history:
            self.cell_history.append(cell_id)

    def get_cell_list(self):
        return list(self.cell_status.keys())

    def get_cell_config(self, cell_id):
        return self.cell_configurations.get(cell_id, None)

    def get_cur_cell_status(self):
        if self.cell_status:
            return self.cell_status[next(iter(self.cell_status))]
        return None

    def get_mobility_history(self):
        return self.cell_history

    def __extract_frequency(self, xml_msg):
        # Extract frequency from XML message
        return 0  # Placeholder for actual implementation

    def __extract_cell_id(self, xml_msg):
        # Extract cell ID from XML message
        return 0  # Placeholder for actual implementation

    def __parse_sib(self, xml_msg):
        # Parse SIB information
        return {'cell_id': 0, 'config': 'sib_config'}  # Placeholder

    def __parse_rrc_reconfig(self, xml_msg):
        # Parse RRC Reconfiguration information
        return {'cell_id': 0, 'config': 'rrc_reconfig'}  # Placeholder

    def __parse_rrc_connection(self, xml_msg):
        # Parse RRC Connection information
        return {'cell_id': 0, 'status': 'connected'}  # Placeholder
