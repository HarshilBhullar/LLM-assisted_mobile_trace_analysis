
from mobile_insight.analyzer.analyzer import Analyzer
import logging
import importlib
import pkgutil


class KPIManagerModified(Analyzer):
    def __init__(self):
        super().__init__()
        self.kpi_analyzers = {}
        self.__check_kpis()
        logging.info("KPIManagerModified initialized with available KPIs: %s", self.list_kpis())

    def __check_kpis(self):
        # Dynamically load KPI analyzers from the mobile_insight.analyzer.kpi module
        kpi_module = importlib.import_module("mobile_insight.analyzer.kpi")
        for _, name, _ in pkgutil.iter_modules(kpi_module.__path__):
            try:
                analyzer_class = getattr(kpi_module, name)
                if issubclass(analyzer_class, Analyzer) and analyzer_class is not Analyzer:
                    self.kpi_analyzers[name] = analyzer_class
            except AttributeError:
                continue

    def list_kpis(self):
        return list(self.kpi_analyzers.keys())

    def enable_kpi(self, kpi_name, periodicity=None, enable_local_storage=False):
        if kpi_name in self.kpi_analyzers:
            kpi_instance = self.kpi_analyzers[kpi_name]()
            kpi_instance.set_source(self.source)
            if periodicity:
                kpi_instance.set_periodicity(periodicity)
            if enable_local_storage:
                kpi_instance.enable_local_storage()
            self.add_analyzer(kpi_instance)
            logging.info("Enabled KPI: %s with periodicity: %s and local storage: %s", kpi_name, periodicity, enable_local_storage)
        else:
            logging.error("KPI %s not found. Available KPIs: %s", kpi_name, self.list_kpis())

    def enable_all_kpis(self):
        for kpi_name in self.kpi_analyzers.keys():
            self.enable_kpi(kpi_name)

    def local_query_kpi(self, kpi_name, mode=None):
        if kpi_name in self.kpi_analyzers:
            logging.info("Querying local KPI: %s with mode: %s", kpi_name, mode)
            # Here should be the logic for querying the KPI, depending on the mode
            kpi_data = {}  # placeholder for actual data
            return kpi_data
        else:
            logging.error("KPI %s not found. Available KPIs: %s", kpi_name, self.list_kpis())
            return None

    def remote_query_kpi(self, kpi_name):
        if kpi_name in self.kpi_analyzers:
            logging.info("Querying remote KPI: %s", kpi_name)
            # Here should be the logic for querying the KPI from a remote service
            kpi_data = {}  # placeholder for actual data
            return kpi_data
        else:
            logging.error("KPI %s not found. Available KPIs: %s", kpi_name, self.list_kpis())
            return None
