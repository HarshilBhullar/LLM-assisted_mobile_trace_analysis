
#!/usr/bin/python
# Filename: kpi_manager_modified.py

"""
A modified KPI Manager with enhanced functionalities for tracking and querying KPIs.
Author: [Your Name]
"""

from mobile_insight.analyzer.analyzer import Analyzer
from mobile_insight.analyzer.kpi import KpiAnalyzer
import logging

__all__ = ["KPIManagerModified"]

class KPIManagerModified(Analyzer):
    """
    An enhanced interface for managing KPIs with additional metrics and functionalities.
    """

    def __init__(self):
        Analyzer.__init__(self)
        self.kpi_analyzers = {}
        self.__check_kpis()
        self.logger = logging.getLogger("KPIManagerModified")

    def __check_kpis(self):
        """
        Dynamically identify and register all available KPIs.
        Associate each KPI name with its corresponding KpiAnalyzer class.
        """
        for kpi_name, kpi_cls in KpiAnalyzer.__subclasses__():
            self.kpi_analyzers[kpi_name] = kpi_cls

    def list_kpis(self):
        """
        Return a list of available KPIs.
        """
        return list(self.kpi_analyzers.keys())

    def enable_kpi(self, kpi_name, periodicity='10m', **kwargs):
        """
        Enable a specific KPI with options to modify its periodicity and settings.

        :param kpi_name: The name of the KPI to enable.
        :param periodicity: The periodicity for KPI monitoring.
        """
        if kpi_name in self.kpi_analyzers:
            kpi_cls = self.kpi_analyzers[kpi_name]
            kpi_instance = kpi_cls()
            kpi_instance.periodicity = periodicity
            for key, value in kwargs.items():
                setattr(kpi_instance, key, value)
            self.add_source_callback(kpi_instance)
            self.logger.info(f"KPI '{kpi_name}' enabled with periodicity {periodicity}.")
        else:
            self.logger.warning(f"KPI '{kpi_name}' not found.")

    def enable_all_kpis(self):
        """
        Enable monitoring for all available KPIs.
        """
        for kpi_name in self.kpi_analyzers:
            self.enable_kpi(kpi_name)

    def local_query_kpi(self, kpi_name, **kwargs):
        """
        Retrieve the locally observed KPI with additional processing.

        :param kpi_name: The name of the KPI to query.
        :returns: Processed KPI data.
        """
        if kpi_name in self.kpi_analyzers:
            # Simulate querying logic, replace with actual implementation
            return f"Locally queried KPI data for {kpi_name}"
        else:
            self.logger.warning(f"KPI '{kpi_name}' not found.")
            return None

    def remote_query_kpi(self, kpi_name, **kwargs):
        """
        Query KPIs from a remote source with additional checks and processing.

        :param kpi_name: The name of the KPI to query.
        :returns: Processed KPI data from remote source.
        """
        # Simulate remote querying logic, replace with actual implementation
        if kpi_name in self.kpi_analyzers:
            return f"Remotely queried KPI data for {kpi_name}"
        else:
            self.logger.warning(f"KPI '{kpi_name}' not found.")
            return None

    def set_source(self, source):
        """
        Set the source of the trace.

        :param source: The trace source.
        :type source: trace collector
        """
        Analyzer.set_source(self, source)
        source.enable_log_all()
