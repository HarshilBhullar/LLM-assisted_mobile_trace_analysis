
#!/usr/bin/python
# Filename: kpi_manager_analysis.py

"""
kpi_manager_analysis.py
An outer analyzer script to evaluate specific KPIs using KPIManager.
"""

# Import necessary modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.kpi import KPIManager

if __name__ == "__main__":

    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path('./logs/')  # Example path for logs

    # Initialize KPIManager
    kpi_manager = KPIManager()

    # Enable specific KPIs with their periodicity settings
    kpi_manager.enable_kpi("KPI.Accessibility.DEDICATED_BEARER_SR_QCI1_REQ", periodicity='10m')
    kpi_manager.enable_kpi("KPI.Accessibility.DEDICATED_BEARER_SR_QCI1_SR", periodicity='10m')
    kpi_manager.enable_kpi("KPI.Accessibility.RRC_SUC", periodicity='5m')
    kpi_manager.enable_kpi("KPI.Accessibility.RRC_SR", periodicity='5m')
    kpi_manager.enable_kpi("KPI.Accessibility.SR_SR", periodicity='10m')
    kpi_manager.enable_kpi("KPI.Accessibility.ATTACH_SR", periodicity='1h')
    kpi_manager.enable_kpi("KPI.Accessibility.HO_SR", periodicity='1h')
    kpi_manager.enable_kpi("KPI.Accessibility.TAU_SR", periodicity='1h')
    kpi_manager.enable_kpi("KPI.Accessibility.RRC_AB_REL", periodicity='10m')
    kpi_manager.enable_kpi("KPI.Wireless.DL_TPUT", periodicity='10m')
    kpi_manager.enable_kpi("KPI.Wireless.BLER", periodicity='10m')

    # Set the KPIManager as the source of the monitor
    kpi_manager.set_source(src)

    # Start the monitoring process
    src.run()

    # Example usage and input paths for testing different KPI scenarios are provided above.
