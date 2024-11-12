
import sys

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.kpi import KPIManager, KpiAnalyzer
import cProfile


def kpi_manager_modified_example(path):

    src = OfflineReplayer()
    src.set_input_path(path)

    kpi_manager = KPIManager()
    
    # Adjusted periodicity and added new KPIs for analysis
    kpi_manager.enable_kpi("KPI.Accessibility.DEDICATED_BEARER_SR_QCI1_REQ", periodicity='5m')
    kpi_manager.enable_kpi("KPI.Accessibility.DEDICATED_BEARER_SR_QCI1_SR", periodicity='1h')
    kpi_manager.enable_kpi("KPI.Accessibility.RRC_SUC", periodicity='30m')
    kpi_manager.enable_kpi("KPI.Accessibility.RRC_SR", cell='22205186', periodicity='30m')
    kpi_manager.enable_kpi("KPI.Accessibility.SR_SR", periodicity='30m')
    kpi_manager.enable_kpi("KPI.Accessibility.ATTACH_SR", periodicity='30m')

    # Test Mobility KPIs with added periodicity
    kpi_manager.enable_kpi("KPI.Mobility.HO_SR", periodicity='30m')
    kpi_manager.enable_kpi("KPI.Mobility.TAU_SR", periodicity='30m')

    # Test Retainability KPIs with an additional KPI
    kpi_manager.enable_kpi("KPI.Retainability.RRC_AB_REL") 
    kpi_manager.enable_kpi("KPI.Retainability.S1_SIG_REL", periodicity='30m')

    # Test Integrity KPIs with adjusted periodicity
    kpi_manager.enable_kpi("KPI.Integrity.DL_TPUT", periodicity='15m') 

    # New Experimental KPIs
    kpi_manager.enable_kpi("KPI.Wireless.BLER")
    kpi_manager.enable_kpi("KPI.Wireless.DL_PDCP_LOSS")
    kpi_manager.enable_kpi("KPI.Wireless.UL_PDCP_LOSS")

    kpi_manager.set_source(src)

    src.run()


if __name__ == '__main__':
    kpi_manager_modified_example(sys.argv[1])
