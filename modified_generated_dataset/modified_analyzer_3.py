
# Usage: python kpi=manager-modified.py [dirname]
# Example1: python kpi-manager-modified.py logs/volte_sample.mi2log 
# Example2: python kpi-manager-modified.py logs/mobility_sample.mi2log 
# Example3: python kpi-manager-modified.py logs/attach_sample.mi2log 
# Example4: python kpi-manager-modified.py logs/data_sample.mi2log 

import sys
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.kpi import KPIManager

def kpi_manager_modified_example(path):
    src = OfflineReplayer()
    src.set_input_path(path)

    kpi_manager = KPIManager()

    # Modified Accessibility KPIs
    kpi_manager.enable_kpi("KPI.Accessibility.DEDICATED_BEARER_SR_QCI1_REQ", periodicity='5m')
    kpi_manager.enable_kpi("KPI.Accessibility.DEDICATED_BEARER_SR_QCI1_SR", periodicity='1h')
    kpi_manager.enable_kpi("KPI.Accessibility.RRC_SUC")
    kpi_manager.enable_kpi("KPI.Accessibility.RRC_SR", cell='22205187')  # Changed cell ID
    kpi_manager.enable_kpi("KPI.Accessibility.SR_SR", periodicity='30m')
    kpi_manager.enable_kpi("KPI.Accessibility.ATTACH_SUC")  # Enabled previously commented KPI

    # Modified Mobility KPIs
    kpi_manager.enable_kpi("KPI.Mobility.HO_SR")
    kpi_manager.enable_kpi("KPI.Mobility.HO_FAILURE", periodicity='30m')  # Enabled previously commented KPI
    kpi_manager.enable_kpi("KPI.Mobility.TAU_SR", periodicity='30m')

    # Modified Retainability KPIs
    kpi_manager.enable_kpi("KPI.Retainability.RRC_AB_REL", periodicity='15m')  # Added periodicity

    # Modified Integrity KPIs
    kpi_manager.enable_kpi("KPI.Integrity.DL_TPUT", threshold='100Mbps')  # Added a threshold parameter for demonstration

    kpi_manager.set_source(src)
    src.run()

if __name__ == '__main__':
    kpi_manager_modified_example(sys.argv[1])
# ### Key Modifications:
# 1. **Periodicity Adjustments**: Changed the periodicity of some KPIs for more frequent analysis.
# 2. **Cell ID Change**: Altered the cell ID for the `KPI.Accessibility.RRC_SR` to demonstrate a different data focus.
# 3. **Enabling Previously Commented KPIs**: Enabled some KPIs that were previously commented out to provide a broader analysis scope.
# 4. **Threshold Parameter**: Introduced a hypothetical `threshold` parameter to the `KPI.Integrity.DL_TPUT` KPI for showcasing how additional parameters might be used.

# This modified analyzer maintains the original structure while introducing new analysis dimensions. Ensure that any new parameters or changes align with the underlying functionality of the `KPIManager` and related classes.