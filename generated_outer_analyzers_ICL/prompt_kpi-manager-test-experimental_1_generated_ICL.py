
#!/usr/bin/python

import sys

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import KPIManager

def kpi_manager_example():
    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path('./logs/offline_log_examples/20201115_181637_Xiaomi-Mi10_46000.mi2log')

    # Initialize KPIManager
    kpi_manager = KPIManager()

    # Enable KPIs
    kpi_manager.enable_kpi('KPI.Wireless.BLER')
    kpi_manager.enable_kpi('KPI.Wireless.DL_PDCP_LOSS')
    kpi_manager.enable_kpi('KPI.Wireless.UL_PDCP_LOSS')
    kpi_manager.enable_kpi('KPI.Mobility.HANDOVER_PREDICTION')
    kpi_manager.enable_kpi('KPI.Mobility.HANDOVER_LATENCY')
    kpi_manager.enable_kpi('KPI.Mobility.HANDOVER_HOL')
    kpi_manager.enable_kpi('KPI.Wireless.DL_TPUT')

    # Set the OfflineReplayer as the data source for KPIManager
    kpi_manager.set_source(src)

    # Start the monitoring
    src.run()

if __name__ == "__main__":
    kpi_manager_example()
