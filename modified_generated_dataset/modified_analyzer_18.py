
import sys

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.kpi import KPIManager, KpiAnalyzer
import cProfile


def modified_kpi_manager_example(path):

    src = OfflineReplayer()
    src.set_input_path(path)

    kpi_manager = KPIManager()
    # print "All supported KPIs:", str(kpi_manager.list_kpis())

    # Test modified KPIs - data plane
    kpi_manager.enable_kpi("KPI.Wireless.BLER") # test log: bler_sample
    kpi_manager.enable_kpi("KPI.Wireless.UL_PDCP_LOSS") # Swapped order for diversity in testing

    # Altered KPI for handover predictions
    kpi_manager.enable_kpi("KPI.Mobility.HANDOVER_PREDICTION", custom_param='new_value') # Assumed custom parameter
    kpi_manager.enable_kpi("KPI.Mobility.HANDOVER_LATENCY") # test log: data_sample

    # Additional KPI for testing
    kpi_manager.enable_kpi("KPI.Accessibility.DEDICATED_BEARER_SR_QCI1_REQ", periodicity='5m') # Reduced periodicity for quick testing

    kpi_manager.set_source(src)

    src.run()


if __name__ == '__main__':
    modified_kpi_manager_example(sys.argv[1])
