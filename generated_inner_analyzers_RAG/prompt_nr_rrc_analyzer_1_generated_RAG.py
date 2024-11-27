
#!/usr/bin/python
# Filename: nr_rrc_analyzer_modified.py

"""
Enhanced NR RRC Analyzer for analyzing 5G NR RRC protocol messages.
"""

from mobile_insight.analyzer.analyzer import ProtocolAnalyzer

__all__ = ["NrRrcAnalyzerModified"]

class NrRrcAnalyzerModified(ProtocolAnalyzer):

    def __init__(self):
        ProtocolAnalyzer.__init__(self)

        self.add_source_callback(self.__rrc_filter)

        # Internal state management
        self.current_cell_status = {}
        self.configuration_history = []
        self.active_configurations = {}

    def set_source(self, source):
        """
        Set the trace source. Enable the NR RRC messages.

        :param source: the trace source (collector).
        """
        ProtocolAnalyzer.set_source(self, source)

        source.enable_log("5G_NR_RRC_OTA_Packet")

    def __rrc_filter(self, msg):
        if msg.type_id == "5G_NR_RRC_OTA_Packet":
            self.__process_rrc_packet(msg)

    def __process_rrc_packet(self, msg):
        log_item = msg.data.decode()

        # Example: Update cell status based on decoded message
        if 'Cell ID' in log_item:
            self.current_cell_status['Cell ID'] = log_item['Cell ID']

        # Example of invoking callbacks based on message type
        if 'RRCConnectionSetupComplete' in log_item['message']:
            self.__callback_rrc_conn(log_item)
        elif 'RRCConnectionReconfiguration' in log_item['message']:
            self.__callback_rrc_reconfig(log_item)
        elif 'SystemInformationBlockType1' in log_item['message']:
            self.__callback_sib_config(log_item)

    def __callback_rrc_conn(self, log_item):
        # Update connectivity status based on RRC Setup Complete
        self.log_info("RRC Connection Setup Complete for Cell ID: " + str(log_item.get('Cell ID')))

    def __callback_rrc_reconfig(self, log_item):
        # Extract and update configurations from RRC Reconfiguration
        if 'MeasConfig' in log_item['message']:
            meas_config = log_item['message']['MeasConfig']
            self.active_configurations['Measurement Config'] = meas_config
            self.configuration_history.append(meas_config)
            self.log_info("Updated Measurement Config: " + str(meas_config))

    def __callback_sib_config(self, log_item):
        # Process SIB configurations (currently unimplemented)
        self.log_info("Received SIB Config for Cell ID: " + str(log_item.get('Cell ID')))

    def get_cell_status(self):
        return self.current_cell_status

    def get_configuration_details(self):
        return self.active_configurations

    def get_mobility_history(self):
        return self.configuration_history
