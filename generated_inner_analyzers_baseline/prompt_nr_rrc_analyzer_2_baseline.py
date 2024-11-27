
from mobileinsight.analyzer import ProtocolAnalyzer
from mobileinsight.analyzer.analyzer import Event

class NrRrcAnalyzerModified(ProtocolAnalyzer):
    def __init__(self):
        super(NrRrcAnalyzerModified, self).__init__()
        self.current_cell_status = None
        self.cell_status_history = []
        self.cell_configurations = {}

        # Register callback for NR RRC OTA Packet
        self.add_source_callback(self.__rrc_filter)

    def __rrc_filter(self, msg):
        if msg.type_id == "5G_NR_RRC_OTA_Packet":
            # Convert msg to XML and process
            xml_msg = msg.data.decode_msg()
            self.__callback_rrc_conn(xml_msg)
            self.__callback_rrc_reconfig(xml_msg)

    def __callback_rrc_conn(self, xml_msg):
        # Dummy implementation to update RRC connection status
        if "rrcConnectionSetupComplete" in xml_msg:
            self.current_cell_status = "Connected"
            self.log_info(f"RRC Connection Setup Complete: {self.current_cell_status}")
        elif "rrcConnectionRelease" in xml_msg:
            self.current_cell_status = "Released"
            self.log_info(f"RRC Connection Released: {self.current_cell_status}")

        # Update cell status history
        self.cell_status_history.append(self.current_cell_status)

    def __callback_rrc_reconfig(self, xml_msg):
        # Dummy implementation to modify configurations
        if "rrcReconfiguration" in xml_msg:
            # Assume some extracted values for demonstration
            freqs = self.__extract_frequencies(xml_msg)
            hysteresis = self.__extract_hysteresis(xml_msg)

            # Modify configurations (dummy calculations)
            modified_freqs = [f * 1.1 for f in freqs]
            modified_hysteresis = hysteresis * 0.9

            # Update configurations
            cell_id = self.__extract_cell_id(xml_msg)
            if cell_id not in self.cell_configurations:
                self.cell_configurations[cell_id] = {}
            self.cell_configurations[cell_id]['frequencies'] = modified_freqs
            self.cell_configurations[cell_id]['hysteresis'] = modified_hysteresis

            self.log_info(f"Updated configuration for cell {cell_id}: Frequencies {modified_freqs}, Hysteresis {modified_hysteresis}")

    def __extract_frequencies(self, xml_msg):
        # Dummy extraction logic
        return [3500, 3600]

    def __extract_hysteresis(self, xml_msg):
        # Dummy extraction logic
        return 3.0

    def __extract_cell_id(self, xml_msg):
        # Dummy extraction logic
        return 1

    def get_current_cell_id(self):
        return self.current_cell_status

    def get_cell_frequency(self, cell_id):
        return self.cell_configurations.get(cell_id, {}).get('frequencies', [])

    def get_cell_hysteresis(self, cell_id):
        return self.cell_configurations.get(cell_id, {}).get('hysteresis', None)

    def get_cell_status_history(self):
        return self.cell_status_history

    def log_info(self, message):
        # Custom logging mechanism
        print(f"[NrRrcAnalyzerModified] {message}")
