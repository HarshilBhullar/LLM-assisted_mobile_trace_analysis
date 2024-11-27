
#!/usr/bin/python
# Filename: nr_rrc_analyzer_modified.py
"""
A modified analyzer for NR RRC protocol

Author: [Your Name]
"""

from .analyzer import ProtocolAnalyzer
import xml.etree.ElementTree as ET
import datetime

class NrRrcAnalyzerModified(ProtocolAnalyzer):
    """
    A modified analyzer for NR RRC protocol
    """

    def __init__(self):
        ProtocolAnalyzer.__init__(self)
        self.add_source_callback(self.__rrc_filter)

        self.current_cell_status = None
        self.cell_status_history = []
        self.cell_configurations = {}

    def set_source(self, source):
        """
        Set the source of the trace.
        Enable NR RRC logs.

        :param source: the source trace collector
        :param type: trace collector
        """
        ProtocolAnalyzer.set_source(self, source)
        source.enable_log("5G_NR_RRC_OTA_Packet")

    def __rrc_filter(self, msg):
        if msg.type_id == "5G_NR_RRC_OTA_Packet":
            log_item = msg.data.decode()
            log_xml = ET.XML(log_item["Msg"])

            self.__callback_rrc_conn(log_xml)
            self.__callback_rrc_reconfig(log_xml)

    def __callback_rrc_conn(self, log_xml):
        for val in log_xml.iter("field"):
            if val.get("name") == "nr-rrc.rrcConnectionSetupComplete":
                self.current_cell_status = "CONNECTED"
                self.cell_status_history.append(self.current_cell_status)
                self.log_info("RRC Connection Setup Complete: CONNECTED")
            elif val.get("name") == "nr-rrc.rrcConnectionRelease":
                self.current_cell_status = "RELEASED"
                self.cell_status_history.append(self.current_cell_status)
                self.log_info("RRC Connection Release: RELEASED")

    def __callback_rrc_reconfig(self, log_xml):
        for val in log_xml.iter("field"):
            if val.get("name") == "nr-rrc.RRCReconfiguration":
                # Extract and modify configurations
                frequency = None
                hysteresis = None
                for config in val.iter("field"):
                    if config.get("name") == "nr-rrc.frequency":
                        frequency = int(config.get("show"))
                    elif config.get("name") == "nr-rrc.hysteresis":
                        hysteresis = float(config.get("show"))
                if frequency and hysteresis:
                    self.cell_configurations[frequency] = {
                        "frequency": frequency,
                        "hysteresis": hysteresis + 0.5  # Example modification
                    }
                    self.log_info(f"Updated RRC Reconfiguration for frequency {frequency}")

    def get_current_cell_id(self):
        return self.current_cell_status

    def get_current_frequency(self):
        return self.current_cell_status

    def get_cell_status_history(self):
        return self.cell_status_history

    def get_cell_configuration(self, frequency):
        return self.cell_configurations.get(frequency, None)
