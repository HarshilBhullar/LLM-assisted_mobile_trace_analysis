
#!/usr/bin/python
# Filename: kpi_manager_modified_example.py

"""
A script demonstrating the usage of KPIManager to track and modify KPI periodicity.
"""

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.kpi import KPIManager


def kpi_manager_modified_example():
    # Initialize the OfflineReplayer
    src = OfflineReplayer()
    src.set_input_path('./logs/offline_log_examples/20201115_181637_Xiaomi-Mi10_46000.mi2log')

    # Initialize KPIManager
    kpi_manager = KPIManager()

    # Print all supported KPIs
    print("All supported KPIs:", kpi_manager.list_kpis())

    # Enable KPIs with specified periodicity and cell configurations
    # Accessibility KPIs
    kpi_manager.enable_kpi("KPI.Accessibility.DEDICATED_BEARER_SR_QCI1_REQ", periodicity='10m')
    kpi_manager.enable_kpi("KPI.Accessibility.RRC_SUC", periodicity='5m')
    kpi_manager.enable_kpi("KPI.Accessibility.RRC_SR", periodicity='5m')
    kpi_manager.enable_kpi("KPI.Accessibility.ATTACH_SR", periodicity='10m')

    # Mobility KPIs
    kpi_manager.enable_kpi("KPI.Mobility.HO_SR", periodicity='10m')
    kpi_manager.enable_kpi("KPI.Mobility.TAU_SR", periodicity='10m')

    # Retainability KPI
    kpi_manager.enable_kpi("KPI.Retainability.RRC_AB_REL", periodicity='5m')

    # Integrity KPIs
    kpi_manager.enable_kpi("KPI.Integrity.DL_TPUT", periodicity='5m')
    kpi_manager.enable_kpi("KPI.Integrity.DL_PDCP_LOSS", periodicity='5m')

    # Set the source for KPIManager
    kpi_manager.set_source(src)

    # Run the OfflineReplayer
    src.run()


if __name__ == '__main__':
    kpi_manager_modified_example()
