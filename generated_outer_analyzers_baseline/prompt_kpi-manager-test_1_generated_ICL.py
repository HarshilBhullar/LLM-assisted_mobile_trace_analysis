
#!/usr/bin/python
# Filename: outer_kpi_analyzer.py

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.kpi import KPIManager

def main():
    # Initialize OfflineReplayer as the data source
    src = OfflineReplayer()
    
    # Set the input path for the trace logs
    # Example: src.set_input_path("/path/to/your/log/file.mi2log")
    src.set_input_path("path/to/your/input.mi2log")
    
    # Initialize KPIManager
    kpi_manager = KPIManager()
    
    # Enable desired KPIs with their respective periodicity
    kpi_manager.enable_kpi("DEDICATED_BEARER_SR_QCI1_REQ", periodicity='5m')
    kpi_manager.enable_kpi("DEDICATED_BEARER_SR_QCI1_SR", periodicity='5m')
    kpi_manager.enable_kpi("RRC_SUC", periodicity='5m')
    kpi_manager.enable_kpi("RRC_SR", periodicity='5m')
    kpi_manager.enable_kpi("SR_SR", periodicity='5m')
    kpi_manager.enable_kpi("ATTACH_SR", periodicity='5m')
    kpi_manager.enable_kpi("HO_SR", periodicity='5m')
    kpi_manager.enable_kpi("TAU_SR", periodicity='5m')
    kpi_manager.enable_kpi("RRC_AB_REL", periodicity='5m')
    kpi_manager.enable_kpi("DL_TPUT", periodicity='5m')
    kpi_manager.enable_kpi("BLER", periodicity='5m')
    
    # Set the data source for KPIManager
    kpi_manager.set_source(src)
    
    # Run the analysis
    src.run()

if __name__ == "__main__":
    main()
