
#!/usr/bin/python
# Filename: kpi_manager_modified.py
"""
kpi_manager_modified.py
An enhanced interface for tracking and querying KPIs with additional functionalities.

Author: Yuanjie Li, Modified by AI Assistant
"""

__all__ = ["KPIManagerModified"]

from ..analyzer import *
import sys, inspect, os


class KPIManagerModified(Analyzer):

    """
    An enhanced interface for tracking and querying KPIs.
    """

    supported_kpis={} # Supported KPIs: kpi_name -> KPIAnalyzer name

    def __init__(self):
        Analyzer.__init__(self)
        self.__check_kpis()

    def __check_kpis(self):
        """
        Find and include all supported KPIs into KPIManager.supported_kpis
        """
        module_tmp = __import__("mobile_insight")
        for item in inspect.getmembers(module_tmp.analyzer.kpi, inspect.isclass):
            if item[1].__bases__[0].__name__ ==  "KpiAnalyzer":
                tmp_module = item[1]()
                for kpi in tmp_module.list_kpis():
                        KPIManagerModified.supported_kpis[kpi] = item[0]
                        self.log_info(kpi)

    def list_kpis(self):
        """
        Return a list of available KPIs 

        :returns: a list of string, each of which is a KPI name
        """
        return list(self.supported_kpis.keys())

    def enable_all_kpis(self, enable_storage = False):
        """
        Enable all KPIs' monitoring
        
        :param enable_storage: Whether to locally store the kpi. False by default
        :type enable_storage: boolean
        """
        for kpi_name in self.list_kpis():
            self.enable_kpi(kpi_name, enable_storage)

    def enable_kpi(self, kpi_name, periodicity='0s', cell=None, enable_storage = True):
        """
        Enable the KPI monitoring with optional modifications

        :param kpi_name: The KPI to be monitored
        :type kpi_name: string
        :param enable_storage: Whether to locally store the kpi. False by default
        :type enable_storage: boolean
        :returns: True if successfully activated, False otherwise
        """

        if kpi_name not in self.supported_kpis:
            self.log_warning("KPI does not exist: "+kpi_name)
            return False

        try: 
            kpi_analyzer_name = self.supported_kpis[kpi_name]
            self.include_analyzer(kpi_analyzer_name, [])
            self.get_analyzer(kpi_analyzer_name).enable_local_storage(enable_storage)
            self.get_analyzer(kpi_analyzer_name).set_periodicity(kpi_name, periodicity)
            self.get_analyzer(kpi_analyzer_name).set_cell(kpi_name, cell)
            # Modification: Adjust periodicity for accessibility KPIs
            if "Accessibility" in kpi_name:
                self.get_analyzer(kpi_analyzer_name).set_periodicity(kpi_name, '10s')
            # Log additional info for KPI activation
            self.log_info(f"Enable KPI: {kpi_name} with periodicity: {periodicity} and storage: {enable_storage}")
            return True
        except Exception as e:
            # Import failure
            self.log_warning("Fail to activate KPI: "+kpi_name)    
            return False

    def local_query_kpi(self, kpi_name, mode = 'cell', timestamp = None):
        """
        Query the phone's locally observed KPI

        :param kpi_name: The KPI to be queried
        :type kpi_name: string
        :param timestamp: The timestamp of the KPI. If None, this function returns the latest KPI
        :type timestamp: datetime
        :returns: The KPI value, or None if the KPI is not available
        """
        if kpi_name not in self.supported_kpis:
            self.log_warning("KPI does not exist: "+kpi_name)
            return None

        kpi_agent = self.get_analyzer(self.supported_kpis[kpi_name])
        if not kpi_agent:
            # KPI analyzer not triggered
            self.log_warning("KPI not activated yet: "+kpi_name)
            self.enable_kpi(kpi_name)
            return None

        # Log query mode
        if mode == 'cell':
            self.log_info(f"Querying KPI: {kpi_name} in cell mode")
        else:
            self.log_info(f"Querying KPI: {kpi_name} in {mode} mode")
        
        return kpi_agent.local_query_kpi(kpi_name, mode, timestamp)

    def remote_query_kpi(self, kpi_name, phone_model, operator, gps, timestamp):
        """
        Query the remote cloud for the KPI

        :param kpi_name: The KPI to be queried
        :type kpi_name: string
        :param phone_model: The phone model
        :type phone_model: string
        :param operator: The network operator
        :type operator: string
        :param gps: The GPS coordinate
        :type gps: string
        :param timestamp: The timestamp of the KPI. 
        :type timestamp: datetime
        :returns: The KPI value, or None if the KPI is not available
        """
        if kpi_name not in KPIManagerModified.supported_kpis:
            self.log_warning("KPI does not exist: "+kpi_name)
            return None

        kpi_agent = self.get_analyzer(KPIManagerModified.supported_kpis[kpi_name])
        if not kpi_agent:
            # KPI analyzer not triggered
            self.log_warning("KPI not activated yet: "+kpi_name)
            self.enable_kpi(kpi_name)
            return None

        # Log additional information for remote query
        self.log_info(f"Remote query for KPI: {kpi_name} at timestamp: {timestamp}")
        
        return kpi_agent.remote_query_kpi(kpi_name, phone_model, operator, gps, timestamp)