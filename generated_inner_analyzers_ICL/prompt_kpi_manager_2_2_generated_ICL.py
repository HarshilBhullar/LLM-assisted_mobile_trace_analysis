
#!/usr/bin/python
# Filename: kpi_manager_modified.py
"""
A modified KPI Manager for enhanced KPI tracking and querying.
Author: Yuanjie Li, Zhehui Zhang
"""

from mobile_insight.analyzer.analyzer import Analyzer
from mobile_insight.analyzer.kpi import KpiAnalyzer
import logging

__all__ = ["KPIManagerModified"]

class KPIManagerModified(Analyzer):
    """
    A modified KPI Manager for managing and querying KPIs.
    """

    def __init__(self):
        Analyzer.__init__(self)

        # Initialize internal states
        self.__kpi_registry = {}
        self.__check_kpis()

    def __check_kpis(self):
        """
        Dynamically identify and register all available KPIs.
        """
        # Example: Register some KPIs for demonstration
        # You should dynamically identify these in a real scenario
        self.__kpi_registry = {
            "KPI.Wireless.BLER": KpiAnalyzer,  # Replace with actual KpiAnalyzer subclass
            "KPI.Wireless.DL_PDCP_LOSS": KpiAnalyzer,  # Replace with actual KpiAnalyzer subclass
            "KPI.Mobility.HANDOVER_PREDICTION": KpiAnalyzer,  # Replace with actual KpiAnalyzer subclass
            # Add more KPIs here as needed
        }

    def list_kpis(self):
        """
        Return a list of available KPIs.
        """
        return list(self.__kpi_registry.keys())

    def enable_all_kpis(self):
        """
        Enable monitoring for all available KPIs.
        """
        for kpi in self.__kpi_registry:
            self.enable_kpi(kpi)

    def enable_kpi(self, kpi_name, periodicity=None, storage=None):
        """
        Activate a specific KPI with options to modify its periodicity and storage settings.

        :param kpi_name: The name of the KPI to enable.
        :param periodicity: Optional periodicity setting.
        :param storage: Optional storage setting.
        """
        if kpi_name in self.__kpi_registry:
            kpi_class = self.__kpi_registry[kpi_name]
            kpi_instance = kpi_class()

            if periodicity:
                kpi_instance.periodicity = periodicity
                kpi_name += "_MOD"

            if storage:
                kpi_instance.storage = storage

            # Set additional attributes like cell information if needed
            # kpi_instance.cell_info = ...

            # Bind KPI instance to the source
            kpi_instance.set_source(self.get_source())
            self.log_info(f"KPI {kpi_name} enabled with periodicity={periodicity} and storage={storage}.")
        else:
            self.log_warning(f"KPI {kpi_name} is not available.")

    def local_query_kpi(self, kpi_name, process_results=False):
        """
        Retrieve the locally observed KPI.

        :param kpi_name: The name of the KPI to query.
        :param process_results: Option to process results further.
        """
        # Example implementation
        # In a real scenario, you would retrieve and process the KPI data
        self.log_info(f"Locally querying KPI: {kpi_name}")

    def remote_query_kpi(self, kpi_name, additional_checks=False):
        """
        Enable querying of KPIs from a remote source.

        :param kpi_name: The name of the KPI to query.
        :param additional_checks: Option to apply additional checks.
        """
        # Example implementation
        # In a real scenario, you would retrieve and process the KPI data
        self.log_info(f"Remotely querying KPI: {kpi_name}")

    def set_source(self, source):
        """
        Set the trace source.

        :param source: The trace source.
        :type source: trace collector
        """
        Analyzer.set_source(self, source)
