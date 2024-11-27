
#!/usr/bin/python
# Filename: kpi_manager_example.py

"""
kpi_manager_example.py
An example script for tracking and logging multiple KPIs using KPIManager
"""

# Import necessary modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.kpi import KPIManager

def kpi_manager_example():
    # Initialize the OfflineReplayer
    src = OfflineReplayer()
    src.set_input_path('./logs/offline_log_examples/20201115_181637_XiaomiMi10_46000.mi2log')

    # Initialize the KPIManager
    kpi_manager = KPIManager()

    # Enable data plane KPIs
    kpi_manager.enable_kpi("KPI.Wireless.BLER")
    kpi_manager.enable_kpi("KPI.Wireless.DL_PDCP_LOSS")
    kpi_manager.enable_kpi("KPI.Wireless.UL_PDCP_LOSS")

    # Enable throughput KPIs
    kpi_manager.enable_kpi("KPI.Wireless.DL_TPUT")
    kpi_manager.enable_kpi("KPI.Wireless.UL_TPUT")

    # Enable mobility KPIs
    kpi_manager.enable_kpi("KPI.Mobility.HANDOVER_PREDICTION")
    kpi_manager.enable_kpi("KPI.Mobility.HANDOVER_LATENCY")
    kpi_manager.enable_kpi("KPI.Mobility.HANDOVER_HOL")

    # Set the KPIManager's source to the OfflineReplayer
    kpi_manager.set_source(src)

    # Run the replay system to process logs
    src.run()

if __name__ == "__main__":
    kpi_manager_example()
