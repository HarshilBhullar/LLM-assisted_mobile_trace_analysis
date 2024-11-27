
#!/usr/bin/python
# Filename: kpi_manager_modified.py
"""
A modified KPI Manager that provides enhanced calculations and logging for KPIs.

Author: Your Name
"""

from mobile_insight.analyzer.analyzer import *
import importlib
import logging

__all__ = ["KPIManagerModified"]

class KPIManagerModified(Analyzer):
    """
    A modified KPI Manager for tracking and querying KPIs with enhanced functionality.
    """

    def __init__(self):
        Analyzer.__init__(self)
        self.kpi_analyzers = {}
        self.__check_kpis()

    def __check_kpis(self):
        """
        Dynamically identify supported KPI analyzers by inspecting the mobile_insight.analyzer.kpi module.
        """
        try:
            kpi_module = importlib.import_module("mobile_insight.analyzer.kpi")
            for name in dir(kpi_module):
                kpi_class = getattr(kpi_module, name)
                if isinstance(kpi_class, type) and issubclass(kpi_class, KpiAnalyzer) and kpi_class is not KpiAnalyzer:
                    self.kpi_analyzers[name] = kpi_class()
            self.log_info("Available KPIs: " + ", ".join(self.kpi_analyzers.keys()))
        except Exception as e:
            self.log_error("Failed to load KPI analyzers: " + str(e))

    def list_kpis(self):
        """
        Returns a list of all available KPI names that can be monitored.
        """
        return list(self.kpi_analyzers.keys())

    def enable_kpi(self, kpi_name, periodicity=None, enable_local_storage=False):
        """
        Enable a specific KPI by its name with optional periodicity and local storage settings.
        """
        if kpi_name in self.kpi_analyzers:
            kpi_analyzer = self.kpi_analyzers[kpi_name]
            kpi_analyzer.enable()
            if periodicity:
                kpi_analyzer.set_periodicity(periodicity)
            kpi_analyzer.enable_local_storage(enable_local_storage)
            self.log_info(f"KPI {kpi_name} enabled with periodicity {periodicity} and local storage {enable_local_storage}")
        else:
            self.log_error(f"KPI {kpi_name} is not available")

    def enable_all_kpis(self):
        """
        Enable monitoring for all identified KPIs.
        """
        for kpi_name in self.kpi_analyzers.keys():
            self.enable_kpi(kpi_name)

    def local_query_kpi(self, kpi_name, mode='default'):
        """
        Query the locally observed KPI values with additional logic based on the mode.
        """
        if kpi_name in self.kpi_analyzers:
            kpi_analyzer = self.kpi_analyzers[kpi_name]
            result = kpi_analyzer.query(mode)
            self.log_info(f"Local query for KPI {kpi_name} with mode {mode}: {result}")
            return result
        else:
            self.log_error(f"KPI {kpi_name} is not available for local querying")
            return None

    def remote_query_kpi(self, kpi_name):
        """
        Query KPI data from a remote cloud service with enhanced logging.
        """
        if kpi_name in self.kpi_analyzers:
            kpi_analyzer = self.kpi_analyzers[kpi_name]
            try:
                result = kpi_analyzer.remote_query()
                self.log_info(f"Remote query for KPI {kpi_name}: {result}")
                return result
            except Exception as e:
                self.log_error(f"Failed to perform remote query for KPI {kpi_name}: {str(e)}")
                return None
        else:
            self.log_error(f"KPI {kpi_name} is not available for remote querying")
            return None

    def set_source(self, source):
        """
        Set the trace source. Enable the KPI analyzers to use the provided source.
        """
        Analyzer.set_source(self, source)
        for kpi_analyzer in self.kpi_analyzers.values():
            kpi_analyzer.set_source(source)
