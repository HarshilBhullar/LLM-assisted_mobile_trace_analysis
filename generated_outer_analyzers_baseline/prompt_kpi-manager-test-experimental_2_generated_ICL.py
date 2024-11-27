
#!/usr/bin/python
# Filename: kpi_manager_test.py

import sys
from mobile_insight.analyzer.offline_replayer import OfflineReplayer
from kpi_manager import KPIManager

def main(log_file_path):
    # Initialize the OfflineReplayer
    src = OfflineReplayer()
    src.set_input_path(log_file_path)

    # Instantiate KPIManager
    kpi_manager = KPIManager()

    # Enable Wireless KPIs
    kpi_manager.enable_kpi("KPI.Wireless.BLER")
    kpi_manager.enable_kpi("KPI.Wireless.DL_PDCP_LOSS")
    kpi_manager.enable_kpi("KPI.Wireless.UL_TPUT")

    # Enable Mobility KPIs with specific configurations
    kpi_manager.enable_kpi("KPI.Mobility.HANDOVER_PREDICTION")
    kpi_manager.enable_kpi("KPI.Mobility.HANDOVER_LATENCY", periodicity='10s')
    kpi_manager.enable_kpi("KPI.Mobility.HANDOVER_HOL", enable_storage=False)

    # Set the source for KPIManager
    kpi_manager.set_source(src)

    # Run the data processing
    src.run()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python kpi_manager_test.py <log_file_path>")
        sys.exit(1)

    log_file_path = sys.argv[1]
    main(log_file_path)
