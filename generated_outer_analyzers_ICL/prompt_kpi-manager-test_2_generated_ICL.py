
#!/usr/bin/python
# Filename: kpi_analysis_script.py

import os
import sys

"""
Script to track and evaluate KPIs using KPIManager
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import KPIManager

def main(input_path):
    try:
        # Initialize a monitor
        src = OfflineReplayer()
        src.set_input_path(input_path)

        # Initialize KPIManager
        kpi_manager = KPIManager()
        kpi_manager.set_source(src)

        # Enable KPIs
        kpi_manager.enable_kpi("DEDICATED_BEARER_SR_QCI1_REQ", periodicity="5m")
        kpi_manager.enable_kpi("DEDICATED_BEARER_SR_QCI1_SR", periodicity="1h")
        kpi_manager.enable_kpi("RRC_SUC")
        kpi_manager.enable_kpi("RRC_SR", cell='22205186')
        kpi_manager.enable_kpi("SR_SR", periodicity="30m")
        kpi_manager.enable_kpi("ATTACH_SR")
        kpi_manager.enable_kpi("HO_SR", periodicity="30m")
        kpi_manager.enable_kpi("TAU_SR", periodicity="30m")
        kpi_manager.enable_kpi("RRC_AB_REL")
        kpi_manager.enable_kpi("DL_TPUT")
        kpi_manager.enable_kpi("BLER")
        kpi_manager.enable_kpi("DL_PDCP_LOSS")
        kpi_manager.enable_kpi("UL_PDCP_LOSS")

        # Start the monitoring
        src.run()

    except Exception as e:
        print(f"Error during KPI analysis: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python kpi_analysis_script.py <input_log_path>")
        sys.exit(1)

    input_log_path = sys.argv[1]
    if not os.path.exists(input_log_path):
        print(f"Log path does not exist: {input_log_path}")
        sys.exit(1)

    main(input_log_path)
