
# Usage: python kpi=manager-modified-test.py [dirname]
# Example1: python kpi-manager-modified-test.py logs/bler_sample.mi2log 
# (For testing KPI BLER with adjusted periodicity)
# Example2: python kpi-manager-modified-test.py logs/data_sample.mi2log 
# (For testing KPI DL_PDCP_LOSS and new KPI HANDOVER_SUCCESS_RATE)

import sys

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.kpi import KPIManager, KpiAnalyzer
import cProfile


def kpi_manager_modified_example(path):

    src = OfflineReplayer()
    src.set_input_path(path)

    kpi_manager = KPIManager()
    # print "All supported KPIs:", str(kpi_manager.list_kpis())

    # Test modified KPIs - data plane
    kpi_manager.enable_kpi("KPI.Wireless.BLER", periodicity='5m')  # Adjusted periodicity
    kpi_manager.enable_kpi("KPI.Wireless.DL_PDCP_LOSS")  # No change
    kpi_manager.enable_kpi("KPI.Wireless.UL_PDCP_LOSS")  # No change

    # Test modified KPIs - handover
    kpi_manager.enable_kpi("KPI.Mobility.HANDOVER_PREDICTION")  # No change
    kpi_manager.enable_kpi("KPI.Mobility.HANDOVER_LATENCY")  # No change
    kpi_manager.enable_kpi("KPI.Mobility.HANDOVER_SUCCESS_RATE")  # New KPI for handover success rate

    kpi_manager.set_source(src)

    src.run()


if __name__ == '__main__':
    kpi_manager_modified_example(sys.argv[1])
