
import sys

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.kpi import KPIManager, KpiAnalyzer
import cProfile


def modified_kpi_manager_example(path):
    src = OfflineReplayer()
    src.set_input_path(path)

    kpi_manager = KPIManager()

    # Adjusted KPI settings
    kpi_manager.enable_kpi("KPI.Accessibility.DEDICATED_BEARER_SR_QCI1_REQ", periodicity='5m')  # Changed periodicity
    kpi_manager.enable_kpi("KPI.Accessibility.DEDICATED_BEARER_SR_QCI1_SR", periodicity='1h')  # Changed periodicity
    kpi_manager.enable_kpi("KPI.Accessibility.RRC_SUC", cell='22205187')  # Changed cell ID
    kpi_manager.enable_kpi("KPI.Accessibility.RRC_SR", cell='22205187')  # Changed cell ID
    kpi_manager.enable_kpi("KPI.Accessibility.SR_SR", periodicity='30m')  # Changed periodicity
    kpi_manager.enable_kpi("KPI.Accessibility.ATTACH_SR")

    # Test Mobility KPIs with alterations
    kpi_manager.enable_kpi("KPI.Mobility.HO_SR")
    kpi_manager.enable_kpi("KPI.Mobility.TAU_SR", periodicity='30m')  # Changed periodicity

    # Removed a Retainability KPI
    # kpi_manager.enable_kpi("KPI.Retainability.RRC_AB_REL")

    # Added additional Integrity KPI
    kpi_manager.enable_kpi("KPI.Integrity.UL_TPUT")  # Added new KPI

    kpi_manager.set_source(src)

    src.run()


if __name__ == '__main__':
    modified_kpi_manager_example(sys.argv[1])
