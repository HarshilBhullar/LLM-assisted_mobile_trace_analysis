
#!/usr/bin/python
# Filename: kpi_manager_example.py

"""
kpi_manager_example.py
An example script to utilize KPIManager for tracking multiple KPIs from mobile network logs

Author: Yuanjie Li
"""

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.kpi import KPIManager
import sys

def main(log_file_path):
    # Create an OfflineReplayer instance
    src = OfflineReplayer()
    src.set_input_path(log_file_path)

    # Create a KPIManager instance
    kpi_manager = KPIManager()

    # Enable specific KPIs
    kpi_manager.enable_kpi("KPI.Wireless.BLER")
    kpi_manager.enable_kpi("KPI.Wireless.DL_PDCP_LOSS")
    kpi_manager.enable_kpi("KPI.Wireless.UL_PDCP_LOSS")
    kpi_manager.enable_kpi("KPI.Wireless.DL_TPUT")
    kpi_manager.enable_kpi("KPI.Wireless.UL_TPUT")
    kpi_manager.enable_kpi("KPI.Mobility.HANDOVER_PREDICTION")
    kpi_manager.enable_kpi("KPI.Mobility.HANDOVER_LATENCY")
    kpi_manager.enable_kpi("KPI.Mobility.HANDOVER_HOL")

    # Set the source for the KPIManager
    kpi_manager.set_source(src)

    # Start the log processing
    src.run()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python kpi_manager_example.py <log_file_path>")
        sys.exit(1)

    log_file_path = sys.argv[1]
    main(log_file_path)
