
#!/usr/bin/python
# Filename: kpi_manager_example.py

"""
An outer analyzer script that utilizes KPIManager to evaluate network KPIs from a log file.
"""

import sys
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.kpi import KPIManager

def kpi_manager_example(log_file_path):
    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path(log_file_path)

    # Initialize KPI Manager
    kpi_manager = KPIManager()
    
    # Enable various KPIs
    kpi_manager.enable_kpi("KPI.Wireless.BLER")
    kpi_manager.enable_kpi("KPI.Wireless.DL_PDCP_LOSS")
    kpi_manager.enable_kpi("KPI.Wireless.UL_PDCP_LOSS")
    kpi_manager.enable_kpi("KPI.Mobility.HANDOVER_PREDICTION")
    kpi_manager.enable_kpi("KPI.Mobility.HANDOVER_LATENCY")
    kpi_manager.enable_kpi("KPI.Mobility.HANDOVER_HOL")
    kpi_manager.enable_kpi("KPI.Wireless.DL_TPUT")

    # Set KPI Manager's source to the monitor
    kpi_manager.set_source(src)

    # Start the monitoring and KPI evaluation
    src.run()

if __name__ == "__main__":
    # Allow for command-line execution
    log_file_path = sys.argv[1] if len(sys.argv) > 1 else './logs/offline_log_examples/20201115_181637_Xiaomi-Mi10_46000.mi2log'
    kpi_manager_example(log_file_path)
