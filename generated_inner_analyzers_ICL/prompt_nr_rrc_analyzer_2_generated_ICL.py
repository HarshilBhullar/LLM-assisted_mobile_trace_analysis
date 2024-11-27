
#!/usr/bin/python
# Filename: nr_rrc_analyzer_modified.py

from mobile_insight.analyzer.analyzer import ProtocolAnalyzer

__all__ = ["NrRrcAnalyzerModified"]

class NrRrcAnalyzerModified(ProtocolAnalyzer):
    def __init__(self):
        ProtocolAnalyzer.__init__(self)
        self.add_source_callback(self.__rrc_filter)

        self.current_cell_status = None
        self.cell_status_history = []
        self.cell_configurations = {}

    def set_source(self, source):
        ProtocolAnalyzer.set_source(self, source)
        source.enable_log("5G_NR_RRC_OTA_Packet")

    def __rrc_filter(self, msg):
        if msg.type_id == "5G_NR_RRC_OTA_Packet":
            self.__process_rrc_packet(msg)

    def __process_rrc_packet(self, msg):
        log_item = msg.data.decode()
        xml_msg = log_item['Msg']
        # Process the XML message to extract RRC connection and configuration details
        # Call the appropriate callback methods based on message content

        if "RRCSetupComplete" in xml_msg or "RRCRelease" in xml_msg:
            self.__callback_rrc_conn(xml_msg)

        if "RRCReconfiguration" in xml_msg:
            self.__callback_rrc_reconfig(xml_msg)

    def __callback_rrc_conn(self, xml_msg):
        # Update RRC connection status
        if "RRCSetupComplete" in xml_msg:
            self.current_cell_status = "Connected"
        elif "RRCRelease" in xml_msg:
            self.current_cell_status = "Idle"

        self.cell_status_history.append(self.current_cell_status)
        self.log_info(f"RRC Connection Status: {self.current_cell_status}")

    def __callback_rrc_reconfig(self, xml_msg):
        # Extract and modify configurations from RRC Reconfiguration messages
        # Update measurement objects, report configurations, etc.
        # Example: update frequency and hysteresis

        frequency = self.__extract_frequency(xml_msg)
        cell_id = self.__extract_cell_id(xml_msg)

        if cell_id not in self.cell_configurations:
            self.cell_configurations[cell_id] = {}

        config = self.cell_configurations[cell_id]
        config['frequency'] = frequency
        config['hysteresis'] = self.__calculate_hysteresis(frequency)

        self.log_info(f"Updated Cell Configuration for Cell ID {cell_id}: {config}")

    def __extract_frequency(self, xml_msg):
        # Extract frequency from the XML message
        # Placeholder logic for extraction
        return 3600

    def __extract_cell_id(self, xml_msg):
        # Extract cell ID from the XML message
        # Placeholder logic for extraction
        return 1

    def __calculate_hysteresis(self, frequency):
        # Modified calculation for hysteresis based on frequency
        return frequency * 0.1

    def get_current_cell_status(self):
        return self.current_cell_status

    def get_cell_status_history(self):
        return self.cell_status_history

    def get_cell_configuration(self, cell_id):
        return self.cell_configurations.get(cell_id, None)
