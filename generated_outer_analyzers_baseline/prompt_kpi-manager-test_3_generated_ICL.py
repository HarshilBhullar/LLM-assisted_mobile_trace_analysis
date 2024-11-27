
#!/usr/bin/python
# Filename: kpi_manager_outer.py

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.kpi.kpi_manager import KPIManager

def kpi_manager_modified_example():
    # Initialize OfflineReplayer
    replayer = OfflineReplayer()
    replayer.set_input_path("path/to/your/input/logfile")  # Set the path to your log file

    # Initialize KPIManager
    kpi_manager = KPIManager()

    # Print all supported KPIs
    print("Supported KPIs:")
    for kpi in kpi_manager.list_kpis():
        print(kpi)

    # Enable selected KPIs with specific periodicity and cell configurations
    kpi_manager.enable_kpi("DEDICATED_BEARER_SR_QCI1_REQ", periodicity='10s')
    kpi_manager.enable_kpi("RRC_SUC", periodicity='10s')
    kpi_manager.enable_kpi("RRC_SR", periodicity='10s')
    kpi_manager.enable_kpi("ATTACH_SR", periodicity='10s')
    kpi_manager.enable_kpi("HO_SR", periodicity='10s')
    kpi_manager.enable_kpi("TAU_SR", periodicity='10s')
    kpi_manager.enable_kpi("RRC_AB_REL", periodicity='10s')
    kpi_manager.enable_kpi("DL_TPUT", periodicity='10s')
    kpi_manager.enable_kpi("DL_PDCP_LOSS", periodicity='10s')  # Experimental KPI

    # Set OfflineReplayer as data source for KPIManager
    kpi_manager.set_source(replayer)

    # Run the replayer
    replayer.run()

if __name__ == "__main__":
    kpi_manager_modified_example()
