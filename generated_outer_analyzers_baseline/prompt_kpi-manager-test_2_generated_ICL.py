
#!/usr/bin/python
# Filename: kpi_analysis_script.py

import sys
import os
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import KPIManager

def main(log_file_path):
    if not os.path.isfile(log_file_path):
        print(f"Error: Log file {log_file_path} does not exist.")
        return
    
    # Initialize the KPIManager
    kpi_manager = KPIManager()
    
    # Set up OfflineReplayer as the data source
    src = OfflineReplayer()
    src.set_input_path(log_file_path)
    
    # Attach the KPIManager to the data source
    kpi_manager.set_source(src)
    
    # Enable Accessibility KPIs
    kpi_manager.enable_kpi("DEDICATED_BEARER_SR_QCI1_REQ", periodicity='5m')
    kpi_manager.enable_kpi("DEDICATED_BEARER_SR_QCI1_SR", periodicity='1h')
    kpi_manager.enable_kpi("RRC_SUC")
    kpi_manager.enable_kpi("RRC_SR", cell='22205186')
    kpi_manager.enable_kpi("SR_SR", periodicity='30m')
    kpi_manager.enable_kpi("ATTACH_SR")
    
    # Enable Mobility KPIs
    kpi_manager.enable_kpi("HO_SR", periodicity='30m')
    kpi_manager.enable_kpi("TAU_SR", periodicity='30m')
    
    # Enable Retainability KPIs
    kpi_manager.enable_kpi("RRC_AB_REL")
    
    # Enable Integrity KPIs
    kpi_manager.enable_kpi("DL_TPUT")
    
    # Enable Experimental KPIs
    kpi_manager.enable_kpi("BLER")
    kpi_manager.enable_kpi("DL_PDCP_LOSS")
    kpi_manager.enable_kpi("UL_PDCP_LOSS")
    
    try:
        # Run the analysis
        src.run()
    except Exception as e:
        print(f"Error: Failed to execute analysis. Details: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python kpi_analysis_script.py <log_file_path>")
    else:
        main(sys.argv[1])
