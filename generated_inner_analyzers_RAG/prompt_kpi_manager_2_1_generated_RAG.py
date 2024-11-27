
#!/usr/bin/python
# Filename: kpi_manager_modified.py

"""
Function: Enhanced interface for tracking and querying KPIs with additional functionalities
Author: [Your Name]
"""

from mobile_insight.analyzer.analyzer import Analyzer
from mobile_insight.analyzer.kpi import KpiAnalyzer
import importlib
import datetime

__all__ = ["KPIManagerModified"]

class KPIManagerModified(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)

        self.kpi_analyzers = {}
        self.__check_kpis()

    def __check_kpis(self):
        """
        Dynamically load all KPI analyzer classes from the mobile_insight.analyzer.kpi module
        and build a dictionary of supported KPIs.
        """
        kpi_module = importlib.import_module('mobile_insight.analyzer.kpi')
        for kpi_name in dir(kpi_module):
            kpi_class = getattr(kpi_module, kpi_name)
            if isinstance(kpi_class, type) and issubclass(kpi_class, KpiAnalyzer):
                kpi_instance = kpi_class()
                self.kpi_analyzers[kpi_instance.name] = kpi_class

    def list_kpis(self):
        """
        Return a list of all available KPI names.
        """
        return list(self.kpi_analyzers.keys())

    def enable_all_kpis(self, local_store=False):
        """
        Enable monitoring for all supported KPIs, with an option to store the KPI data locally.
        """
        for kpi_name in self.kpi_analyzers:
            self.enable_kpi(kpi_name, local_store=local_store)

    def enable_kpi(self, kpi_name, periodicity=None, local_store=False):
        """
        Activate monitoring for a specific KPI, with options for modifying behavior such as periodicity.
        Includes error handling for unsupported KPIs.
        """
        if kpi_name not in self.kpi_analyzers:
            self.log_warning(f"KPI {kpi_name} is not supported.")
            return

        kpi_instance = self.kpi_analyzers[kpi_name]()
        kpi_instance.set_source(self.get_source())

        if periodicity:
            kpi_instance.set_periodicity(periodicity)

        if local_store:
            kpi_instance.enable_local_store()

        if "Accessibility" in kpi_name:
            kpi_instance.set_periodicity('30m')  # Modified calculation for accessibility KPIs

        self.log_info(f"KPI {kpi_name} has been enabled.")

    def local_query_kpi(self, kpi_name, timestamp=None):
        """
        Query the locally observed KPI value based on the specified name and optionally a timestamp.
        """
        try:
            kpi_instance = self.kpi_analyzers[kpi_name]()
            return kpi_instance.query(timestamp)
        except KeyError:
            self.log_warning(f"KPI {kpi_name} has not been enabled.")
        except Exception as e:
            self.log_warning(f"Failed to query KPI {kpi_name}: {str(e)}")

    def remote_query_kpi(self, kpi_name, phone_model=None, operator=None, gps=None, timestamp=None):
        """
        Query the remote cloud service for KPI values, based on various parameters.
        """
        # Placeholder for remote query implementation
        self.log_info(f"Querying remote KPI {kpi_name} with parameters: "
                      f"phone_model={phone_model}, operator={operator}, gps={gps}, timestamp={timestamp}")

    def set_source(self, source):
        """
        Set the trace source for the analyzer.
        """
        Analyzer.set_source(self, source)
        self.log_info("Trace source has been set for KPI Manager.")
