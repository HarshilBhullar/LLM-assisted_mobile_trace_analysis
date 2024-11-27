
from mobile_insight.analyzer.analyzer import Analyzer
from mobile_insight.analyzer.kpi import KpiAnalyzer
import logging

class KPIManagerModified(Analyzer):
    def __init__(self):
        super(KPIManagerModified, self).__init__()
        self.supported_kpis = {}
        self.__check_kpis()

    def __check_kpis(self):
        # Discover all KPI analyzers
        for subclass in KpiAnalyzer.__subclasses__():
            self.supported_kpis[subclass.__name__] = subclass
        logging.info(f"Supported KPIs: {list(self.supported_kpis.keys())}")

    def list_kpis(self):
        return list(self.supported_kpis.keys())

    def enable_all_kpis(self, enable_storage=False):
        for kpi_name in self.list_kpis():
            try:
                self.enable_kpi(kpi_name)
            except Exception as e:
                logging.warning(f"Failed to enable KPI {kpi_name}: {str(e)}")

    def enable_kpi(self, kpi_name, periodicity='5s'):
        if kpi_name not in self.supported_kpis:
            logging.warning(f"KPI {kpi_name} is not supported.")
            return
        try:
            kpi_class = self.supported_kpis[kpi_name]
            kpi_instance = kpi_class()
            kpi_instance.set_source(self.get_source())
            kpi_instance.set_periodicity(periodicity)
            kpi_instance.enable()
            logging.info(f"Enabled KPI {kpi_name} with periodicity {periodicity}")
        except Exception as e:
            logging.warning(f"Exception enabling KPI {kpi_name}: {str(e)}")

    def local_query_kpi(self, kpi_name):
        if kpi_name not in self.supported_kpis:
            logging.warning(f"KPI {kpi_name} is not supported.")
            return None
        try:
            kpi_instance = self.supported_kpis[kpi_name]()
            if not kpi_instance.is_enabled():
                self.enable_kpi(kpi_name)
            result = kpi_instance.query()
            return f"Local query for {kpi_name}: {result} (modified)"
        except Exception as e:
            logging.warning(f"Exception querying KPI {kpi_name}: {str(e)}")
            return None

    def remote_query_kpi(self, kpi_name):
        if kpi_name not in self.supported_kpis:
            logging.warning(f"KPI {kpi_name} is not supported.")
            return None
        try:
            kpi_instance = self.supported_kpis[kpi_name]()
            if not kpi_instance.is_enabled():
                self.enable_kpi(kpi_name)
            result = kpi_instance.remote_query()
            return f"Remote query for {kpi_name}: {result} (modified)"
        except Exception as e:
            logging.warning(f"Exception querying KPI {kpi_name}: {str(e)}")
            return None
