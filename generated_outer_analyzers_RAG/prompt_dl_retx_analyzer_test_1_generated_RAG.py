
#!/usr/bin/python
# Filename: lte_dl_retx_analysis.py

"""
Script to analyze downlink MAC and RLC retransmission delays using LteDlRetxAnalyzer.
"""

import sys
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import LteDlRetxAnalyzer

def my_analysis():
    try:
        # Initialize the OfflineReplayer
        src = OfflineReplayer()
        src.set_input_path('./logs/offline_log_examples/20201115_181637_Xiaomi-Mi10_46000.mi2log')

        # Initialize the LteDlRetxAnalyzer
        lte_analyzer = LteDlRetxAnalyzer()
        lte_analyzer.set_source(src)

        # Execute the analysis
        src.run()

        # Calculate average and maximum delays
        mac_delay_total = 0.0
        mac_delay_count = 0
        mac_delay_max = 0.0

        rlc_delay_total = 0.0
        rlc_delay_count = 0
        rlc_delay_max = 0.0

        for _, bearer in lte_analyzer.bearer_entity.items():
            for item in bearer.mac_retx:
                mac_delay_total += item['mac_retx']
                mac_delay_count += 1
                if item['mac_retx'] > mac_delay_max:
                    mac_delay_max = item['mac_retx']

            for item in bearer.rlc_retx:
                rlc_delay_total += item['rlc_retx']
                rlc_delay_count += 1
                if item['rlc_retx'] > rlc_delay_max:
                    rlc_delay_max = item['rlc_retx']

        avg_mac_delay = mac_delay_total / mac_delay_count if mac_delay_count > 0 else 0.0
        avg_rlc_delay = rlc_delay_total / rlc_delay_count if rlc_delay_count > 0 else 0.0

        print("Average MAC retransmission delay is:", avg_mac_delay)
        print("Maximum MAC retransmission delay is:", mac_delay_max)
        print("Average RLC retransmission delay is:", avg_rlc_delay)
        print("Maximum RLC retransmission delay is:", rlc_delay_max)

    except Exception as e:
        print("An error occurred during analysis:", str(e))


if __name__ == "__main__":
    my_analysis()
