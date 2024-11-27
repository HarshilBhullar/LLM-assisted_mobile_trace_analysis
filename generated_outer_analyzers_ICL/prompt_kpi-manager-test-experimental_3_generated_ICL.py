
#!/usr/bin/python
# Filename: kpi_manager_example.py
import os
import sys

"""
Example of using KPIManager to track KPIs from mobile network logs
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.kpi import KPIManager

if __name__ == "__main__":

    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")

    # Initialize the KPI Manager
    kpi_manager = KPIManager()
    
    # Enable specific KPIs for analysis
    kpi_manager.enable_kpi("KPI.Wireless.BLER")
    kpi_manager.enable_kpi("KPI.Wireless.DL_PDCP_LOSS")
    kpi_manager.enable_kpi("KPI.Wireless.UL_PDCP_LOSS")
    kpi_manager.enable_kpi("KPI.Wireless.DL_TPUT")
    kpi_manager.enable_kpi("KPI.Wireless.UL_TPUT")
    kpi_manager.enable_kpi("KPI.Mobility.HANDOVER_PREDICTION")
    kpi_manager.enable_kpi("KPI.Mobility.HANDOVER_LATENCY")
    kpi_manager.enable_kpi("KPI.Mobility.HANDOVER_HOL")

    # Set the source for the KPI Manager
    kpi_manager.set_source(src)

    # Start the monitoring
    src.run()
