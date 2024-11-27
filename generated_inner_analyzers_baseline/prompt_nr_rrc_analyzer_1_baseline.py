
from mobile_insight.analyzer import ProtocolAnalyzer
import logging

class NrRrcAnalyzerModified(ProtocolAnalyzer):
    def __init__(self):
        super(NrRrcAnalyzerModified, self).__init__()
        self.add_source_callback(self.__rrc_filter)
        self.current_cell_status = {}
        self.config_history = []
        self.active_configurations = {}
        logging.basicConfig(level=logging.INFO)

    def set_source(self, source):
        """
        Enable 5G_NR_RRC_OTA_Packet from the source.
        """
        self.source = source
        self.source.enable_log("5G_NR_RRC_OTA_Packet")

    def __rrc_filter(self, msg):
        """
        Filter and process 5G_NR_RRC_OTA_Packet messages.
        """
        if msg.type_id == "5G_NR_RRC_OTA_Packet":
            decoded_msg = msg.decode()
            self.update_cell_status(decoded_msg)
            self.__callback_rrc_conn(decoded_msg)
            self.__callback_rrc_reconfig(decoded_msg)

    def update_cell_status(self, decoded_msg):
        """
        Update current cell status based on the decoded message.
        """
        cell_id = decoded_msg.get('CellId', None)
        if cell_id:
            self.current_cell_status['CellId'] = cell_id
            logging.info(f"Updated cell status: {self.current_cell_status}")

    def __callback_rrc_conn(self, decoded_msg):
        """
        Handle RRC connection updates.
        """
        if 'RRCSetupComplete' in decoded_msg:
            self.current_cell_status['RRC_Status'] = 'Connected'
            logging.info("RRC Connection Setup Complete.")
        elif 'RRCRelease' in decoded_msg:
            self.current_cell_status['RRC_Status'] = 'Released'
            logging.info("RRC Connection Released.")

    def __callback_rrc_reconfig(self, decoded_msg):
        """
        Handle RRC Reconfiguration messages.
        """
        if 'RRCReconfiguration' in decoded_msg:
            config_id = decoded_msg.get('ConfigId', None)
            if config_id:
                self.active_configurations[config_id] = decoded_msg
                self.config_history.append(decoded_msg)
                logging.info(f"Updated RRC Reconfiguration: {self.active_configurations}")

    def __callback_sib_config(self, decoded_msg):
        """
        Handle System Information Block configurations (currently unimplemented).
        """
        pass

    def get_current_cell_status(self):
        """
        Return the current cell status.
        """
        return self.current_cell_status

    def get_configuration_details(self):
        """
        Return details of active configurations.
        """
        return self.active_configurations

    def get_mobility_history(self):
        """
        Return the configuration history.
        """
        return self.config_history
