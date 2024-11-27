
#!/usr/bin/python

import sys
import traceback

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import LteDlRetxAnalyzer


def my_analysis(input_path):
    try:
        # Initialize the OfflineReplayer with the provided input path
        src = OfflineReplayer()
        src.set_input_path(input_path)

        # Initialize the LteDlRetxAnalyzer and set the source
        lteAnalyzer = LteDlRetxAnalyzer()
        lteAnalyzer.set_source(src)

        # Run the analyzer
        src.run()

        # Initialize variables to calculate average and maximum delays
        mac_delay_total = 0.0
        mac_delay_sample = 0
        rlc_delay_total = 0.0
        rlc_delay_sample = 0
        max_mac_delay = 0.0
        max_rlc_delay = 0.0

        # Collect retransmission data for each radio bearer
        for _, bearer in lteAnalyzer.bearer_entity.items():
            for item in bearer.mac_retx:
                mac_delay_total += item['mac_retx']
                mac_delay_sample += 1
                if item['mac_retx'] > max_mac_delay:
                    max_mac_delay = item['mac_retx']

            for item in bearer.rlc_retx:
                rlc_delay_total += item['rlc_retx']
                rlc_delay_sample += 1
                if item['rlc_retx'] > max_rlc_delay:
                    max_rlc_delay = item['rlc_retx']

        # Calculate average delays
        avg_mac_delay = mac_delay_total / mac_delay_sample if mac_delay_sample > 0 else 0.0
        avg_rlc_delay = rlc_delay_total / rlc_delay_sample if rlc_delay_sample > 0 else 0.0

        # Print the calculated statistics
        print("Average MAC retransmission delay is:", avg_mac_delay)
        print("Average RLC retransmission delay is:", avg_rlc_delay)
        print("Maximum MAC retransmission delay is:", max_mac_delay)
        print("Maximum RLC retransmission delay is:", max_rlc_delay)

    except Exception as e:
        print("An error occurred during analysis:")
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python lte_dl_retx_analysis.py <input_file_path>")
    else:
        my_analysis(sys.argv[1])
