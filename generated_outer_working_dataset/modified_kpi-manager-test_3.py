
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


def kpi_manager_modified_example():

    src = OfflineReplayer()
    src.set_input_path('./logs/offline_log_examples/20201115_181637_Xiaomi-Mi10_46000.mi2log')

    kpi_manager = KPIManager()
    # print "All supported KPIs:", str(kpi_manager.list_kpis())

    # Modifying the periodicity of some KPIs and adding a new KPI for analysis
    kpi_manager.enable_kpi("KPI.Accessibility.DEDICATED_BEARER_SR_QCI1_REQ", periodicity='5m')
    kpi_manager.enable_kpi("KPI.Accessibility.DEDICATED_BEARER_SR_QCI1_SR", periodicity='1h')
    kpi_manager.enable_kpi("KPI.Accessibility.RRC_SUC", periodicity='30m')
    kpi_manager.enable_kpi("KPI.Accessibility.RRC_SR", cell='22205186', periodicity='15m')
    # kpi_manager.enable_kpi("KPI.Accessibility.SR_SUC", periodicity='1h')
    kpi_manager.enable_kpi("KPI.Accessibility.SR_SR", periodicity='30m')
    # kpi_manager.enable_kpi("KPI.Accessibility.ATTACH_SUC")
    kpi_manager.enable_kpi("KPI.Accessibility.ATTACH_SR", periodicity='45m')

    # Test Mobility KPIs
    # kpi_manager.enable_kpi("KPI.Mobility.HO_TOTAL")
    kpi_manager.enable_kpi("KPI.Mobility.HO_SR", periodicity='2h')
    # kpi_manager.enable_kpi("KPI.Mobility.HO_TOTAL", periodicity='1h')
    # kpi_manager.enable_kpi("KPI.Mobility.HO_FAILURE", periodicity='1h')
    kpi_manager.enable_kpi("KPI.Mobility.TAU_SR", periodicity='2h')
    # kpi_manager.enable_kpi("KPI.Mobility.TAU_REQ", periodicity='1h')

    # Test Retainability KPIs
    kpi_manager.enable_kpi("KPI.Retainability.RRC_AB_REL", periodicity='1h') 

    # Test Integrity KPIs
    kpi_manager.enable_kpi("KPI.Integrity.DL_TPUT", periodicity='10m')
    # Adding an experimental KPI for demonstration
    kpi_manager.enable_kpi("KPI.Integrity.DL_PDCP_LOSS", periodicity='5m') 

    kpi_manager.set_source(src)

    src.run()


if __name__ == '__main__':
    kpi_manager_modified_example()
