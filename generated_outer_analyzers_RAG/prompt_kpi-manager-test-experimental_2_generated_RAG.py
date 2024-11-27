
#!/usr/bin/python
# Filename: kpi_manager_test.py

import sys
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.kpi import KPIManager

def kpi_manager_example(log_file_path):
    src = OfflineReplayer()
    src.set_input_path(log_file_path)

    kpi_manager = KPIManager()

    # Enable Wireless KPIs
    kpi_manager.enable_kpi("KPI.Wireless.BLER")
    kpi_manager.enable_kpi("KPI.Wireless.DL_PDCP_LOSS")
    kpi_manager.enable_kpi("KPI.Wireless.UL_TPUT")  # Hypothetical additional KPI

    # Enable Mobility KPIs
    kpi_manager.enable_kpi("KPI.Mobility.HANDOVER_PREDICTION")
    kpi_manager.enable_kpi("KPI.Mobility.HANDOVER_LATENCY", periodicity='5m')  # Increased periodicity
    kpi_manager.enable_kpi("KPI.Mobility.HANDOVER_HOL", enable_storage=False)  # Disable local storage

    kpi_manager.set_source(src)

    src.run()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python kpi_manager_test.py [log_file_path]")
        sys.exit(1)
    
    log_file_path = sys.argv[1]
    kpi_manager_example(log_file_path)
