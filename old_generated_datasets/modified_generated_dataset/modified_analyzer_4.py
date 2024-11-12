
# Usage: python kpi=manager-test.py [dirname]
# Example1: python kpi-manager-test-experimental.py logs/bler_sample.mi2log 
# (For testing KPI BLER)
# Example2: python kpi-manager-test-experimental.py logs/data_sample.mi2log 
# (For testing KPI DL_PDCP_LOSS, HANDOVER_PREDICTION, HANDOVER_LATENCY, HANDOVER_HOL)
# import os
import sys

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.kpi import KPIManager, KpiAnalyzer
import cProfile


def kpi_manager_modified_example(path):

    src = OfflineReplayer()
    src.set_input_path(path)

    kpi_manager = KPIManager()
    # print "All supported KPIs:", str(kpi_manager.list_kpis())

    # Test experimental KPIs - data plane with a modified periodicity
    kpi_manager.enable_kpi("KPI.Wireless.BLER", periodicity='5m') # test log: bler_sample
    kpi_manager.enable_kpi("KPI.Wireless.DL_PDCP_LOSS", periodicity='5m') # test log: data_sample
    kpi_manager.enable_kpi("KPI.Wireless.UL_PDCP_LOSS", periodicity='5m')

    # Test experimental KPIs - handover with a different set of metrics
    kpi_manager.enable_kpi("KPI.Mobility.HANDOVER_PREDICTION", periodicity='5m') # test log: data_sample
    kpi_manager.enable_kpi("KPI.Mobility.HANDOVER_LATENCY", periodicity='5m') # test log: data_sample
    kpi_manager.enable_kpi("KPI.Mobility.HANDOVER_SUCCESS_RATE") # added new KPI metric

    kpi_manager.set_source(src)

    src.run()


if __name__ == '__main__':
    kpi_manager_modified_example(sys.argv[1])
