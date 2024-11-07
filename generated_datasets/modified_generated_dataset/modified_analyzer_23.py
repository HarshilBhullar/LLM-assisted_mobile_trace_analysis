
# Usage: python kpi=manager-test-modified.py [dirname]
# Example1: python kpi-manager-test-modified.py logs/volte_sample.mi2log 
# (For testing KPI DEDICATED_BEARER_SR_QCI1)
# Example2: python kpi-manager-test-modified.py logs/mobility_sample.mi2log 
# (For testing KPI RRC, SR, TAU, HO)
# Example3: python kpi-manager-test-modified.py logs/attach_sample.mi2log 
# (For testing KPI ATTACH)
# Example4: python kpi-manager-test-modified.py logs/data_sample.mi2log 
# (For testing KPI DL_TPUT)
# import os
import sys

from mobile_insight.monitor import OfflineReplayer
# from mobile_insight.analyzer import LteMacAnalyzer, LtePdcpGapAnalyzer
from mobile_insight.analyzer.kpi import KPIManager, KpiAnalyzer
import cProfile


def kpi_manager_modified_example(path):

    src = OfflineReplayer()
    src.set_input_path(path)

    kpi_manager = KPIManager()
    # print "All supported KPIs:", str(kpi_manager.list_kpis())

    kpi_manager.enable_kpi("KPI.Accessibility.DEDICATED_BEARER_SR_QCI1_REQ", periodicity='5m')
    kpi_manager.enable_kpi("KPI.Accessibility.DEDICATED_BEARER_SR_QCI1_SR", periodicity='1h')
    kpi_manager.enable_kpi("KPI.Accessibility.RRC_SUC", cell='22205187')
    kpi_manager.enable_kpi("KPI.Accessibility.RRC_SR", periodicity='30m')
    # kpi_manager.enable_kpi("KPI.Accessibility.SR_SUC", periodicity='1h')
    kpi_manager.enable_kpi("KPI.Accessibility.SR_SR", periodicity='30m')
    # kpi_manager.enable_kpi("KPI.Accessibility.ATTACH_SUC")
    kpi_manager.enable_kpi("KPI.Accessibility.ATTACH_SR", periodicity='2h')

    # Test Mobility KPIs
    # kpi_manager.enable_kpi("KPI.Mobility.HO_TOTAL")
    kpi_manager.enable_kpi("KPI.Mobility.HO_SR", periodicity='2h')
    # kpi_manager.enable_kpi("KPI.Mobility.HO_TOTAL", periodicity='1h')
    # kpi_manager.enable_kpi("KPI.Mobility.HO_FAILURE", periodicity='1h')
    kpi_manager.enable_kpi("KPI.Mobility.TAU_SR", periodicity='30m')
    # kpi_manager.enable_kpi("KPI.Mobility.TAU_REQ", periodicity='1h')

    # Test Retainability KPIs
    kpi_manager.enable_kpi("KPI.Retainability.RRC_AB_REL", cell='22205188') 

    # Test Integrity KPIs
    kpi_manager.enable_kpi("KPI.Integrity.DL_TPUT", periodicity='15m') 

    kpi_manager.set_source(src)

    src.run()


if __name__ == '__main__':
    kpi_manager_modified_example(sys.argv[1])
