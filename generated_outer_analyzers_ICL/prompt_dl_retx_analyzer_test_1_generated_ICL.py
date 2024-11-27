
#!/usr/bin/python
# Filename: lte_dl_retx_analysis.py
import os
import sys

"""
Offline analysis for downlink MAC and RLC retransmission delays
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import LteDlRetxAnalyzer

def my_analysis():
    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")

    lte_dl_retx_analyzer = LteDlRetxAnalyzer()
    lte_dl_retx_analyzer.set_source(src)

    try:
        # Start the monitoring
        src.run()

        # Analyze retransmission delays
        def analyze_retransmission_delays(analyzer):
            total_mac_delay, total_rlc_delay = 0, 0
            max_mac_delay, max_rlc_delay = 0, 0
            mac_count, rlc_count = 0, 0

            for bearer in analyzer.bearer_entity.values():
                for entry in bearer.mac_retx:
                    total_mac_delay += entry['mac_retx']
                    max_mac_delay = max(max_mac_delay, entry['mac_retx'])
                    mac_count += 1

                for entry in bearer.rlc_retx:
                    total_rlc_delay += entry['rlc_retx']
                    max_rlc_delay = max(max_rlc_delay, entry['rlc_retx'])
                    rlc_count += 1

            avg_mac_delay = total_mac_delay / mac_count if mac_count > 0 else 0
            avg_rlc_delay = total_rlc_delay / rlc_count if rlc_count > 0 else 0

            return avg_mac_delay, max_mac_delay, avg_rlc_delay, max_rlc_delay

        avg_mac_delay, max_mac_delay, avg_rlc_delay, max_rlc_delay = analyze_retransmission_delays(lte_dl_retx_analyzer)
        print(f"Average MAC Retransmission Delay: {avg_mac_delay} ms, Maximum MAC Retransmission Delay: {max_mac_delay} ms")
        print(f"Average RLC Retransmission Delay: {avg_rlc_delay} ms, Maximum RLC Retransmission Delay: {max_rlc_delay} ms")

    except Exception as e:
        print(f"An error occurred during analysis: {e}")

if __name__ == "__main__":
    my_analysis()
