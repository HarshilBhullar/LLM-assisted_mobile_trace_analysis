
#!/usr/bin/python
# Filename: modified-offline-analysis-example.py

import os
import sys

"""
Modified offline analysis by replaying logs
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import LteDlRetxAnalyzer

if __name__ == "__main__":

    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")  # Specify the path to your log files
    # src.enable_log_all()

    # Instantiate the LteDlRetxAnalyzer and set its source
    lte_dl_retx_analyzer = LteDlRetxAnalyzer()
    lte_dl_retx_analyzer.set_source(src)

    # Start the analysis
    src.run()

    # Calculate metrics
    total_mac_delay = 0.0
    mac_sample_count = 0
    total_rlc_delay = 0.0
    rlc_sample_count = 0
    max_mac_delay = 0.0
    max_rlc_delay = 0.0

    for _, bearer in lte_dl_retx_analyzer.bearer_entity.items():
        for item in bearer.mac_retx:
            mac_delay = item['mac_retx']
            total_mac_delay += mac_delay
            mac_sample_count += 1
            if mac_delay > max_mac_delay:
                max_mac_delay = mac_delay

        for item in bearer.rlc_retx:
            rlc_delay = item['rlc_retx']
            total_rlc_delay += rlc_delay
            rlc_sample_count += 1
            if rlc_delay > max_rlc_delay:
                max_rlc_delay = rlc_delay

    avg_mac_delay = total_mac_delay / mac_sample_count if mac_sample_count > 0 else 0.0
    avg_rlc_delay = total_rlc_delay / rlc_sample_count if rlc_sample_count > 0 else 0.0

    # Print the results
    print(f"Average MAC retransmission delay: {avg_mac_delay} ms")
    print(f"Maximum MAC retransmission delay: {max_mac_delay} ms")
    print(f"Average RLC retransmission delay: {avg_rlc_delay} ms")
    print(f"Maximum RLC retransmission delay: {max_rlc_delay} ms")
