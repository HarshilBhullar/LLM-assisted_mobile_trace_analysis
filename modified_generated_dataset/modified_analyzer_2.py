# Usage: python kpi=manager-modified.py [dirname]
# Example1: python kpi-manager-modified.py logs/bler_sample.mi2log 
# (For testing KPI BLER and UL_PDCP_LOSS)
# Example2: python kpi-manager-modified.py logs/data_sample.mi2log 
# (For testing KPI DL_PDCP_LOSS, HANDOVER_EFFICIENCY, HANDOVER_LATENCY)

import sys
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.kpi import KPIManager

def kpi_manager_modified_example(path):
    src = OfflineReplayer()
    src.set_input_path(path)
    
    kpi_manager = KPIManager()
    
    # Test adjusted KPIs - data plane
    kpi_manager.enable_kpi("KPI.Wireless.BLER", periodicity='5m')  # Adjusted periodicity
    kpi_manager.enable_kpi("KPI.Wireless.UL_PDCP_LOSS")  # Removed DL_PDCP_LOSS for this test

    # Test adjusted KPIs - handover
    kpi_manager.enable_kpi("KPI.Mobility.HANDOVER_EFFICIENCY")  # New KPI for testing handover efficiency
    kpi_manager.enable_kpi("KPI.Mobility.HANDOVER_LATENCY")

    kpi_manager.set_source(src)
    src.run()

if __name__ == '__main__':
    kpi_manager_modified_example(sys.argv[1])
# ### Key Modifications:
# 1. **Adjusted Periodicity**: Changed the periodicity of "KPI.Wireless.BLER" to '5m' from its default setting.
# 2. **New KPI**: Added a new KPI "KPI.Mobility.HANDOVER_EFFICIENCY" to demonstrate different handover metrics.
# 3. **Removed KPI**: Removed "KPI.Wireless.DL_PDCP_LOSS" from one of the test cases to focus on uplink analysis.

# This modified analyzer remains consistent with the codebase's style and structure, ensuring it integrates seamlessly with existing components. Adjustments to the KPIs and their configurations allow for different slices of data analysis, which can be useful for varied test scenarios.