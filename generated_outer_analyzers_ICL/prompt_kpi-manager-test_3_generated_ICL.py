
#!/usr/bin/python
# Filename: kpi_manager_modified_example.py
import os
import sys

"""
KPI Management example using the KPIManager class
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import KPIManager

def kpi_manager_modified_example():
    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")
    
    # Initialize KPIManager
    kpi_manager = KPIManager()
    
    # List and print all supported KPIs
    supported_kpis = kpi_manager.list_kpis()
    print("Supported KPIs:")
    for kpi in supported_kpis:
        print(kpi)

    # Enable KPIs with specified periodicity
    kpi_manager.enable_kpi("DEDICATED_BEARER_SR_QCI1_REQ", "5s")
    kpi_manager.enable_kpi("RRC_SUC", "5s")
    kpi_manager.enable_kpi("RRC_SR", "5s")
    kpi_manager.enable_kpi("ATTACH_SR", "5s")
    kpi_manager.enable_kpi("HO_SR", "5s")
    kpi_manager.enable_kpi("TAU_SR", "5s")
    kpi_manager.enable_kpi("RRC_AB_REL", "5s")
    kpi_manager.enable_kpi("DL_TPUT", "5s")
    kpi_manager.enable_kpi("DL_PDCP_LOSS", "5s")

    # Set the source for KPIManager
    kpi_manager.set_source(src)

    # Run the replay
    src.run()

if __name__ == "__main__":
    kpi_manager_modified_example()
