
# Usage: python kpi=manager-modified-test.py [dirname]
# Example1: python kpi-manager-modified-test.py logs/bler_sample.mi2log 
# (For modified testing KPI BLER)
# Example2: python kpi-manager-modified-test.py logs/data_sample.mi2log 
# (For modified testing KPI DL_PDCP_LOSS, HANDOVER_PREDICTION, HANDOVER_LATENCY, HANDOVER_HOL)
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

    # Modified KPIs - data plane
    kpi_manager.enable_kpi("KPI.Wireless.BLER", threshold=0.05) # Adjusted threshold for BLER
    kpi_manager.enable_kpi("KPI.Wireless.DL_PDCP_LOSS") # test log: data_sample
    kpi_manager.enable_kpi("KPI.Wireless.UL_PDCP_LOSS", periodicity='5m') # Changed periodicity

    # Modified KPIs - handover
    kpi_manager.enable_kpi("KPI.Mobility.HANDOVER_PREDICTION") # test log: data_sample
    kpi_manager.enable_kpi("KPI.Mobility.HANDOVER_LATENCY", latency_threshold=100) # Added latency threshold
    kpi_manager.enable_kpi("KPI.Mobility.HANDOVER_HOL") # test log: data_sample

    kpi_manager.set_source(src)

    src.run()


if __name__ == '__main__':
    kpi_manager_modified_example(sys.argv[1])
