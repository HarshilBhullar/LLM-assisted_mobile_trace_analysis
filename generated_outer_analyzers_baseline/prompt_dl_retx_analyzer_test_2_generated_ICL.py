
#!/usr/bin/python
# Filename: my_analysis.py

"""
Function: Analyze LTE downlink MAC and RLC retransmission delays
Author: Qianru Li
"""

from mobile_insight.monitor import OfflineReplayer
from lte_dl_retx_analyzer import LteDlRetxAnalyzer
import sys

def my_analysis(input_file):
    try:
        # Initialize the OfflineReplayer
        src = OfflineReplayer()
        src.set_input_path(input_file)
        
        # Initialize the LteDlRetxAnalyzer
        analyzer = LteDlRetxAnalyzer()
        analyzer.set_source(src)
        
        # Run the analyzer
        src.run()

        # Calculate average and maximum retransmission delays
        for cfg_idx, entity in analyzer.bearer_entity.items():
            if entity.mac_retx:
                mac_retx_delays = [retx['mac_retx'] for retx in entity.mac_retx]
                avg_mac_retx_delay = sum(mac_retx_delays) / len(mac_retx_delays)
                max_mac_retx_delay = max(mac_retx_delays)
                print(f"Bearer {cfg_idx}: Average MAC Retransmission Delay: {avg_mac_retx_delay:.2f}, Max MAC Retransmission Delay: {max_mac_retx_delay}")
            else:
                print(f"Bearer {cfg_idx}: No MAC Retransmission Delays")

            if entity.rlc_retx:
                rlc_retx_delays = [retx['rlc_retx'] for retx in entity.rlc_retx]
                avg_rlc_retx_delay = sum(rlc_retx_delays) / len(rlc_retx_delays)
                max_rlc_retx_delay = max(rlc_retx_delays)
                print(f"Bearer {cfg_idx}: Average RLC Retransmission Delay: {avg_rlc_retx_delay:.2f}, Max RLC Retransmission Delay: {max_rlc_retx_delay}")
            else:
                print(f"Bearer {cfg_idx}: No RLC Retransmission Delays")

    except Exception as e:
        print(f"Error during analysis: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python my_analysis.py <input_log>")
        sys.exit(1)

    input_file = sys.argv[1]
    my_analysis(input_file)
