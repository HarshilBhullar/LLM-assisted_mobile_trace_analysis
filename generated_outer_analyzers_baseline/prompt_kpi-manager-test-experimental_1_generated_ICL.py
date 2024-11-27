
#!/usr/bin/python
# Filename: outer_analyzer.py

import sys
from mobile_insight.monitor import OfflineReplayer
from kpi_manager import KPIManager

def kpi_manager_example(log_file_path):
    # Initialize OfflineReplayer
    src = OfflineReplayer()
    src.set_input_path(log_file_path)

    # Initialize KPIManager
    kpi_manager = KPIManager()

    # Enable various KPIs
    kpi_manager.enable_kpi('KPI.Wireless.BLER')
    kpi_manager.enable_kpi('KPI.Wireless.DL_PDCP_LOSS')
    kpi_manager.enable_kpi('KPI.Wireless.UL_PDCP_LOSS')
    kpi_manager.enable_kpi('KPI.Mobility.HANDOVER_PREDICTION')
    kpi_manager.enable_kpi('KPI.Mobility.HANDOVER_LATENCY')
    kpi_manager.enable_kpi('KPI.Mobility.HANDOVER_HOL')
    kpi_manager.enable_kpi('KPI.Wireless.DL_TPUT')

    # Set OfflineReplayer as the data source for KPIManager
    kpi_manager.set_source(src)

    # Run the OfflineReplayer to process the log file
    src.run()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python outer_analyzer.py <log_file_path>")
    else:
        log_file_path = sys.argv[1]
        kpi_manager_example(log_file_path)
