#!/usr/bin/python

import sys
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import LteDlRetxAnalyzer

if __name__ == "__main__":
    src = OfflineReplayer()
    src.set_input_path(sys.argv[1])

    lteAnalyzer = LteDlRetxAnalyzer()
    lteAnalyzer.set_source(src)

    src.run()

    mac_delay = 0.0
    mac_delay_sample = 0

    rlc_delay = 0.0
    rlc_delay_sample = 0

    # New metrics for standard deviation
    mac_delay_squared_sum = 0.0
    rlc_delay_squared_sum = 0.0

    for _, bearer in lteAnalyzer.bearer_entity.items():
        for item in bearer.mac_retx:
            mac_retx_value = item['mac_retx']
            mac_delay += mac_retx_value
            mac_delay_squared_sum += mac_retx_value ** 2
        mac_delay_sample += len(bearer.mac_retx)

        for item in bearer.rlc_retx:
            rlc_retx_value = item['rlc_retx']
            rlc_delay += rlc_retx_value
            rlc_delay_squared_sum += rlc_retx_value ** 2
        rlc_delay_sample += len(bearer.rlc_retx)

    avg_mac_delay = float(mac_delay) / mac_delay_sample if mac_delay_sample > 0 else 0.0
    avg_rlc_delay = float(rlc_delay) / rlc_delay_sample if rlc_delay_sample > 0 else 0.0

    # Calculate standard deviation for MAC and RLC retx delays
    mac_std_dev = (
        (mac_delay_squared_sum / mac_delay_sample - avg_mac_delay ** 2) ** 0.5
        if mac_delay_sample > 0 else 0.0
    )
    rlc_std_dev = (
        (rlc_delay_squared_sum / rlc_delay_sample - avg_rlc_delay ** 2) ** 0.5
        if rlc_delay_sample > 0 else 0.0
    )

    print("Average MAC retx delay is: ", avg_mac_delay)
    print("MAC retx delay standard deviation is: ", mac_std_dev)
    print("Average RLC retx delay is:", avg_rlc_delay)
    print("RLC retx delay standard deviation is: ", rlc_std_dev)

# ### Explanation of Changes:
# 1. **Standard Deviation Calculation**: Added standard deviation calculations for both MAC and RLC retransmission delays. This involves calculating the squared sum of delays and using the formula for standard deviation.

# 2. **Variable Naming**: Introduced new variables `mac_delay_squared_sum` and `rlc_delay_squared_sum` to accumulate the squares of the delays.

# 3. **Output**: Added print statements to display the standard deviation alongside the average delay.

# These modifications provide additional insights into the variability of the retransmission delays, which could be useful for analyzing network performance. The code remains consistent with the existing codebase's style and structure.