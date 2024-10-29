
import sys

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.kpi import KPIManager
import cProfile

def modified_kpi_manager_example(path):

    src = OfflineReplayer()
    src.set_input_path(path)

    kpi_manager = KPIManager()

    # Enable a different set of KPIs with modified periodicity and additional KPIs
    kpi_manager.enable_kpi("KPI.Accessibility.DEDICATED_BEARER_SR_QCI1_REQ", periodicity='15m')
    kpi_manager.enable_kpi("KPI.Accessibility.DEDICATED_BEARER_SR_QCI1_SR", periodicity='1h')
    kpi_manager.enable_kpi("KPI.Accessibility.RRC_SUC")
    kpi_manager.enable_kpi("KPI.Accessibility.RRC_SR", cell='22205186')
    kpi_manager.enable_kpi("KPI.Accessibility.SR_SR", periodicity='30m')
    kpi_manager.enable_kpi("KPI.Accessibility.ATTACH_SR")

    # Include additional Mobility KPIs
    kpi_manager.enable_kpi("KPI.Mobility.HO_SR")
    kpi_manager.enable_kpi("KPI.Mobility.TAU_SR", periodicity='30m')
    kpi_manager.enable_kpi("KPI.Mobility.TAU_REQ", periodicity='30m')

    # Test Retainability KPIs with an additional metric
    kpi_manager.enable_kpi("KPI.Retainability.RRC_AB_REL")
    kpi_manager.enable_kpi("KPI.Retainability.CALL_DROP_RATE", periodicity='1h')

    # Test Integrity KPIs with a focus on uplink throughput
    kpi_manager.enable_kpi("KPI.Integrity.DL_TPUT")
    kpi_manager.enable_kpi("KPI.Integrity.UL_TPUT", periodicity='10m')

    kpi_manager.set_source(src)

    src.run()

if __name__ == '__main__':
    modified_kpi_manager_example(sys.argv[1])
