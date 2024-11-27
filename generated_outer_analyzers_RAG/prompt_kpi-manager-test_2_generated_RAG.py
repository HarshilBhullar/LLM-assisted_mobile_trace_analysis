
#!/usr/bin/python

import sys
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.kpi import KPIManager

def kpi_analysis(log_file_path):
    try:
        # Initialize OfflineReplayer
        src = OfflineReplayer()
        src.set_input_path(log_file_path)

        # Initialize KPIManager
        kpi_manager = KPIManager()

        # Enable Accessibility KPIs
        kpi_manager.enable_kpi("KPI.Accessibility.DEDICATED_BEARER_SR_QCI1_REQ", periodicity='5m')
        kpi_manager.enable_kpi("KPI.Accessibility.DEDICATED_BEARER_SR_QCI1_SR", periodicity='1h')
        kpi_manager.enable_kpi("KPI.Accessibility.RRC_SUC")
        kpi_manager.enable_kpi("KPI.Accessibility.RRC_SR", cell='22205186')
        kpi_manager.enable_kpi("KPI.Accessibility.SR_SR", periodicity='30m')
        kpi_manager.enable_kpi("KPI.Accessibility.ATTACH_SR")

        # Enable Mobility KPIs
        kpi_manager.enable_kpi("KPI.Mobility.HO_SR")
        kpi_manager.enable_kpi("KPI.Mobility.TAU_SR", periodicity='30m')

        # Enable Retainability KPIs
        kpi_manager.enable_kpi("KPI.Retainability.RRC_AB_REL")

        # Enable Integrity KPIs
        kpi_manager.enable_kpi("KPI.Integrity.DL_TPUT")

        # Enable Experimental KPIs
        kpi_manager.enable_kpi("KPI.Wireless.BLER")
        kpi_manager.enable_kpi("KPI.Wireless.DL_PDCP_LOSS")
        kpi_manager.enable_kpi("KPI.Wireless.UL_PDCP_LOSS")

        # Set the data source
        kpi_manager.set_source(src)

        # Run the analysis
        src.run()

    except Exception as e:
        print(f"Error during KPI analysis: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python script_name.py [log_file_path]")
        sys.exit(1)

    log_file_path = sys.argv[1]
    kpi_analysis(log_file_path)
