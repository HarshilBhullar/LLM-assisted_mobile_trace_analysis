
# Usage: python kpi=manager-modified-test.py [dirname]
# Example1: python kpi-manager-modified-test.py logs/bler_sample.mi2log 
# (For testing KPI BLER with adjusted periodicity)
# Example2: python kpi-manager-modified-test.py logs/data_sample.mi2log 
# (For testing KPI DL_PDCP_LOSS and a custom KPI)
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

    # Test experimental KPIs with modified settings
    kpi_manager.enable_kpi("KPI.Wireless.BLER", periodicity='5m') # Adjusted periodicity for BLER
    kpi_manager.enable_kpi("KPI.Wireless.DL_PDCP_LOSS")  # Unchanged
    kpi_manager.enable_kpi("KPI.Wireless.UL_PDCP_LOSS")

    # Adding a custom KPI calculation
    kpi_manager.enable_kpi("KPI.Custom.NEW_METRIC") # An example custom KPI

    # Test experimental KPIs - handover with modified settings
    kpi_manager.enable_kpi("KPI.Mobility.HANDOVER_PREDICTION") # Unchanged
    kpi_manager.enable_kpi("KPI.Mobility.HANDOVER_LATENCY", periodicity='15m') # Adjusted periodicity
    kpi_manager.enable_kpi("KPI.Mobility.HANDOVER_HOL") # Unchanged

    kpi_manager.set_source(src)

    src.run()


if __name__ == '__main__':
    kpi_manager_modified_example(sys.argv[1])
