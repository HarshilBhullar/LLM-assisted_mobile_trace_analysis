
# Usage: python kpi=manager-test-modified.py [dirname]
# Example1: python kpi-manager-test-modified.py logs/bler_sample.mi2log 
# (For testing KPI BLER with modifications)
# Example2: python kpi-manager-test-modified.py logs/data_sample.mi2log 
# (For testing modified KPIs)

import sys

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.kpi import KPIManager
import cProfile


def kpi_manager_modified_example():

    src = OfflineReplayer()
    src.set_input_path('./logs/offline_log_examples/20201115_181637_Xiaomi-Mi10_46000.mi2log')

    kpi_manager = KPIManager()
    # print "All supported KPIs:", str(kpi_manager.list_kpis())

    # Modified experimental KPIs - data plane
    kpi_manager.enable_kpi("KPI.Wireless.BLER")  # test log: bler_sample
    kpi_manager.enable_kpi("KPI.Wireless.DL_PDCP_LOSS")  # test log: data_sample

    # Additional KPI for uplink throughput
    kpi_manager.enable_kpi("KPI.Wireless.UL_TPUT")  # Assumed additional test log

    # Modified experimental KPIs - handover
    kpi_manager.enable_kpi("KPI.Mobility.HANDOVER_PREDICTION")  # test log: data_sample
    kpi_manager.enable_kpi("KPI.Mobility.HANDOVER_LATENCY", periodicity='5m')  # Increased periodicity
    kpi_manager.enable_kpi("KPI.Mobility.HANDOVER_HOL", enable_storage=False)  # Disable local storage

    kpi_manager.set_source(src)

    src.run()


if __name__ == '__main__':
    kpi_manager_modified_example()
