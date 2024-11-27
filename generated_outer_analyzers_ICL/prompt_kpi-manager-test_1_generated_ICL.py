
#!/usr/bin/python
# Filename: kpi_analysis.py

"""
KPI Analysis using KPIManager from kpi_manager.py
"""

# Import necessary modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.kpi import KPIManager

def main():
    # Initialize OfflineReplayer as the data source
    src = OfflineReplayer()
    src.set_input_path("./logs/")  # Set input path for log files

    # Initialize KPIManager
    kpi_manager = KPIManager()

    # Enable various KPIs
    kpi_manager.enable_kpi("DEDICATED_BEARER_SR_QCI1_REQ", periodicity='5m')
    kpi_manager.enable_kpi("DEDICATED_BEARER_SR_QCI1_SR", periodicity='5m')
    kpi_manager.enable_kpi("RRC_SUC", periodicity='1h')
    kpi_manager.enable_kpi("RRC_SR", periodicity='10m')
    kpi_manager.enable_kpi("SR_SR", periodicity='10m')
    kpi_manager.enable_kpi("ATTACH_SR", periodicity='10m')
    kpi_manager.enable_kpi("HO_SR", periodicity='10m')
    kpi_manager.enable_kpi("TAU_SR", periodicity='10m')
    kpi_manager.enable_kpi("RRC_AB_REL", periodicity='10m')
    kpi_manager.enable_kpi("DL_TPUT", periodicity='10m')
    kpi_manager.enable_kpi("BLER", periodicity='10m')

    # Set the data source for KPIManager
    kpi_manager.set_source(src)

    # Run the analysis
    src.run()

if __name__ == "__main__":
    main()
