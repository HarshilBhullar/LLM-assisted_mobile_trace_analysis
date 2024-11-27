
#!/usr/bin/python
# Filename: kpi_manager_modified.py
"""
A modified KPI manager that provides an enhanced interface for tracking and querying KPIs

"""

from mobile_insight.analyzer.analyzer import Analyzer
from mobile_insight.analyzer.kpi import KpiAnalyzer
import logging

__all__ = ["KPIManagerModified"]

class KPIManagerModified(Analyzer):

    def __init__(self):
        Analyzer.__init__(self)

        self.supported_kpis = {}
        self.__check_kpis()

    def __check_kpis(self):
        """
        Populate the supported_kpis dictionary with available KPI analyzers
        """
        for subclass in KpiAnalyzer.__subclasses__():
            class_name = subclass.__name__
            kpi_name = class_name.replace('Analyzer', '').upper()
            self.supported_kpis[kpi_name] = class_name

    def list_kpis(self):
        """
        List all available KPI names
        :return: list of KPI names
        """
        return list(self.supported_kpis.keys())

    def enable_all_kpis(self, enable_storage=False):
        """
        Enable monitoring for all KPIs
        :param enable_storage: whether to store KPIs locally
        """
        for kpi in self.supported_kpis.keys():
            self.enable_kpi(kpi, enable_storage)

    def enable_kpi(self, kpi_name, enable_storage=False, periodicity='5s'):
        """
        Enable monitoring for a specific KPI
        :param kpi_name: KPI name
        :param enable_storage: whether to store KPI locally
        :param periodicity: periodicity setting for KPI
        """
        try:
            # Fake method to simulate enabling a KPI
            # Actual implementation will depend on how KPI enabling is managed
            logging.info(f"Enabling KPI: {kpi_name} with periodicity {periodicity}")
            # Simulate possible exception
            # raise Exception("KPI could not be enabled")
        except Exception as e:
            logging.warning(f"Could not enable KPI {kpi_name}: {e}")

    def local_query_kpi(self, kpi_name):
        """
        Query a locally observed KPI
        :param kpi_name: KPI name
        :return: modified result string
        """
        if kpi_name not in self.supported_kpis:
            self.enable_kpi(kpi_name)
        # Fake query result
        result = f"Local KPI {kpi_name} result"
        return f"Modified Local Query Result: {result}"

    def remote_query_kpi(self, kpi_name):
        """
        Query a KPI from a remote cloud
        :param kpi_name: KPI name
        :return: modified result string
        """
        if kpi_name not in self.supported_kpis:
            self.enable_kpi(kpi_name)
        # Fake query result
        result = f"Remote KPI {kpi_name} result"
        return f"Modified Remote Query Result: {result}"
