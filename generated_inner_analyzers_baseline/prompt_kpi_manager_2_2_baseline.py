
from mobile_insight.analyzer import Analyzer
from mobile_insight.analyzer.kpi import KpiAnalyzer
import logging

class KPIManagerModified(Analyzer):
    def __init__(self):
        super(KPIManagerModified, self).__init__()
        self.kpi_registry = {}
        self.__check_kpis()
        self.enabled_kpis = {}

    def __check_kpis(self):
        # Dynamically identify and register all available KPIs
        for name, cls in KpiAnalyzer.__subclasses__():
            self.kpi_registry[name] = cls

    def list_kpis(self):
        # Return a list of available KPIs
        return list(self.kpi_registry.keys())

    def enable_all_kpis(self):
        # Enable monitoring for all available KPIs
        for kpi in self.kpi_registry.keys():
            self.enable_kpi(kpi)

    def enable_kpi(self, kpi_name, periodicity=None, storage_path=None, cell_info=None):
        # Activate a specific KPI, modify its periodicity and storage
        if kpi_name in self.kpi_registry:
            kpi_instance = self.kpi_registry[kpi_name]()
            if periodicity:
                kpi_name = kpi_name + '_MOD'
                kpi_instance.set_periodicity(periodicity)
            if storage_path:
                kpi_instance.set_storage_path(storage_path)
            if cell_info:
                kpi_instance.set_cell_info(cell_info)
            self.enabled_kpis[kpi_name] = kpi_instance
            logging.info(f"KPI {kpi_name} enabled with periodicity {periodicity} and storage {storage_path}")
        else:
            logging.error(f"KPI {kpi_name} not found in registry.")

    def local_query_kpi(self, kpi_name, process_func=None):
        # Retrieve locally observed KPI
        if kpi_name in self.enabled_kpis:
            result = self.enabled_kpis[kpi_name].get_results()
            if process_func:
                result = process_func(result)
            return result
        else:
            logging.error(f"KPI {kpi_name} is not enabled.")
            return None

    def remote_query_kpi(self, kpi_name, remote_source, process_func=None):
        # Query KPIs from a remote source
        # This is a placeholder for remote query logic
        try:
            if kpi_name in self.kpi_registry:
                # Assume some remote fetch logic here
                result = {}  # Replace with actual fetching logic
                if process_func:
                    result = process_func(result)
                return result
            else:
                logging.error(f"KPI {kpi_name} not found in registry.")
                return None
        except Exception as e:
            logging.error(f"Error querying KPI {kpi_name} remotely: {str(e)}")
            return None

    def set_source(self, source):
        # Set the data source for KPI analysis
        self.source = source
        for kpi in self.enabled_kpis.values():
            kpi.set_source(self.source)

    def run(self):
        # Execute the analysis
        self.source.run()
