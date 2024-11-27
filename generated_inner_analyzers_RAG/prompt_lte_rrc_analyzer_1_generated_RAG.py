
#!/usr/bin/python
# Filename: lte_rrc_analyzer_modified.py
"""
A modified analyzer for LTE RRC protocol with additional metrics

Author: Yuanjie Li (Modified)
"""

from mobile_insight.analyzer.analyzer import ProtocolAnalyzer

__all__ = ["LteRrcAnalyzerModified"]

class LteRrcAnalyzerModified(ProtocolAnalyzer):

    def __init__(self):
        ProtocolAnalyzer.__init__(self)

        self.add_source_callback(self.__rrc_filter)

        self.current_cell_status = None
        self.cell_history = []
        self.configurations = {}

    def set_source(self, source):
        """
        Set the trace source. Enable the LTE RRC messages

        :param source: the trace source (collector).
        """
        ProtocolAnalyzer.set_source(self, source)
        source.enable_log("LTE_RRC_OTA_Packet")
        source.enable_log("LTE_RRC_Serv_Cell_Info")
        source.enable_log("LTE_RRC_CDRX_Events_Info")

    def create_state_machine(self):
        """
        Create a state machine for LTE RRC states
        """
        pass  # Implement state machine logic here

    def __rrc_filter(self, msg):
        """
        Process incoming LTE RRC messages
        """
        if msg.type_id == "LTE_RRC_OTA_Packet":
            self.__callback_rrc_reconfig(msg)
        elif msg.type_id == "LTE_RRC_Serv_Cell_Info":
            self.__callback_sib_config(msg)

    def __callback_sib_config(self, msg):
        """
        Extract configurations from System Information Blocks (SIBs)
        """
        log_item = msg.data.decode()
        # Extract and log radio assessment thresholds and preference settings
        self.log_info(f"SIB Configurations: {log_item}")

        # Update internal states
        self.configurations.update(log_item)

    def __callback_rrc_reconfig(self, msg):
        """
        Process RRC Reconfiguration messages
        """
        log_item = msg.data.decode()
        # Extract measurement profiles and configurations
        self.log_info(f"RRC Reconfiguration: {log_item}")

        # Broadcast relevant information
        self.current_cell_status = log_item.get("Cell Status")
        self.cell_history.append(self.current_cell_status)

        # Update internal states
        self.configurations.update(log_item)
