
#!/usr/bin/python
# Filename: kpi_manager_modified.py
"""
A modified KPI manager with enhanced logging and additional functionality for KPI tracking and querying.
"""

from mobile_insight.analyzer.analyzer import *
from mobile_insight.analyzer.kpi import KPIManager, KpiAnalyzer
import inspect

__all__ = ["KPIManagerModified"]

class KPIManagerModified(Analyzer):

    def __init__(self):
        Analyzer.__init__(self)
        self.kpi_analyzers = {}
        self.__check_kpis()

    def __check_kpis(self):
        """
        Inspect the mobile_insight.analyzer.kpi module to identify supported KPI analyzers.
        """
        kpi_module = inspect.getmembers(sys.modules['mobile_insight.analyzer.kpi'], inspect.isclass)
        for name, obj in kpi_module:
            if issubclass(obj, KpiAnalyzer) and obj is not KpiAnalyzer:
                self.kpi_analyzers[name] = obj
        self.log_info("Available KPIs: " + str(self.list_kpis()))

    def list_kpis(self):
        """
        Return a list of available KPIs.
        """
        return list(self.kpi_analyzers.keys())

    def enable_kpi(self, kpi_name, periodicity='1m', local_storage=True):
        """
        Enable a specific KPI by its name with additional logging.

        :param kpi_name: The name of the KPI to enable.
        :param periodicity: The periodicity for KPI calculation.
        :param local_storage: Whether to enable local storage for the KPI data.
        """
        if kpi_name in self.kpi_analyzers:
            kpi_instance = self.kpi_analyzers[kpi_name]()
            kpi_instance.set_source(self.get_source())
            kpi_instance.enable_periodicity(periodicity)
            kpi_instance.enable_local_storage(local_storage)
            kpi_instance.start()
            self.log_info(f"KPI {kpi_name} enabled with periodicity {periodicity} and local storage set to {local_storage}.")
        else:
            self.log_error(f"KPI {kpi_name} not found in available KPIs.")

    def enable_all_kpis(self):
        """
        Enable all identified KPIs.
        """
        for kpi_name in self.list_kpis():
            self.enable_kpi(kpi_name)

    def local_query_kpi(self, kpi_name, mode='default'):
        """
        Query locally observed KPI values with modified logic and logging.

        :param kpi_name: The name of the KPI to query.
        :param mode: The mode for querying (e.g., 'cell').
        :return: Queried KPI data.
        """
        result = None
        if kpi_name in self.kpi_analyzers:
            kpi_instance = self.kpi_analyzers[kpi_name]()
            result = kpi_instance.local_query(mode)
            self.log_info(f"Local query for KPI {kpi_name} in mode {mode}: {result}")
        else:
            self.log_error(f"KPI {kpi_name} not found in available KPIs.")
        return result

    def remote_query_kpi(self, kpi_name):
        """
        Query KPI data from a remote cloud service with enhanced logging.

        :param kpi_name: The name of the KPI to query.
        :return: Queried KPI data from the remote service.
        """
        result = None
        if kpi_name in self.kpi_analyzers:
            kpi_instance = self.kpi_analyzers[kpi_name]()
            result = kpi_instance.remote_query()
            self.log_info(f"Remote query for KPI {kpi_name}: {result}")
        else:
            self.log_error(f"KPI {kpi_name} not found in available KPIs.")
        return result

    def set_source(self, source):
        """
        Set the trace source for the analyzer.
        """
        Analyzer.set_source(self, source)
        self.log_info("Trace source set for KPI Manager.")
