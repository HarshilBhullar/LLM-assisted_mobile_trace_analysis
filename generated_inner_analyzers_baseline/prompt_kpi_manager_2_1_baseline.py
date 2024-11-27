
from mobile_insight.analyzer import Analyzer
from mobile_insight.analyzer.kpi import KpiAnalyzer
import importlib

class KPIManagerModified(Analyzer):
    
    def __init__(self):
        super(KPIManagerModified, self).__init__()
        self.kpi_analyzers = {}
        self.active_kpis = {}
        self.__check_kpis()
    
    def __check_kpis(self):
        try:
            kpi_module = importlib.import_module("mobile_insight.analyzer.kpi")
            for name, cls in kpi_module.__dict__.items():
                if isinstance(cls, type) and issubclass(cls, KpiAnalyzer) and cls is not KpiAnalyzer:
                    self.kpi_analyzers[name] = cls
        except ImportError as e:
            self.log_warning("Failed to import KPI analyzers: %s" % str(e))

    def list_kpis(self):
        return list(self.kpi_analyzers.keys())

    def enable_all_kpis(self, store_locally=False):
        for kpi_name in self.kpi_analyzers:
            self.enable_kpi(kpi_name, store_locally)

    def enable_kpi(self, kpi_name, store_locally=False, periodicity=None):
        if kpi_name not in self.kpi_analyzers:
            self.log_warning("KPI %s is not supported." % kpi_name)
            return
        if kpi_name in self.active_kpis:
            self.log_info("KPI %s is already enabled." % kpi_name)
            return

        kpi_instance = self.kpi_analyzers[kpi_name]()
        kpi_instance.set_source(self.get_source())
        
        if "Accessibility" in kpi_name:
            periodicity = periodicity or 60  # Adjust periodicity for accessibility KPIs

        if periodicity:
            kpi_instance.set_periodicity(periodicity)

        kpi_instance.set_store_local(store_locally)
        self.active_kpis[kpi_name] = kpi_instance
        self.log_info("Enabled KPI: %s" % kpi_name)

    def local_query_kpi(self, kpi_name, timestamp=None):
        if kpi_name not in self.active_kpis:
            self.log_warning("KPI %s is not active. Attempting to enable it now." % kpi_name)
            self.enable_kpi(kpi_name)
            if kpi_name not in self.active_kpis:
                self.log_warning("Failed to enable KPI %s." % kpi_name)
                return None

        kpi_instance = self.active_kpis[kpi_name]
        return kpi_instance.query_local(timestamp)

    def remote_query_kpi(self, kpi_name, phone_model=None, operator=None, gps=None, timestamp=None):
        if kpi_name not in self.active_kpis:
            self.log_warning("KPI %s is not active. Attempting to enable it now." % kpi_name)
            self.enable_kpi(kpi_name)
            if kpi_name not in self.active_kpis:
                self.log_warning("Failed to enable KPI %s." % kpi_name)
                return None

        kpi_instance = self.active_kpis[kpi_name]
        return kpi_instance.query_remote(phone_model, operator, gps, timestamp)
