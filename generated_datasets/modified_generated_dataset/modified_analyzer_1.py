
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

    # New metric: sum of squared delays for variance calculation
    mac_delay_squared = 0.0
    rlc_delay_squared = 0.0

    for _, bearer in lteAnalyzer.bearer_entity.items():
        for item in bearer.mac_retx:
            mac_delay += item['mac_retx']
            mac_delay_squared += item['mac_retx'] ** 2
        mac_delay_sample += len(bearer.mac_retx)

        for item in bearer.rlc_retx:
            rlc_delay += item['rlc_retx']
            rlc_delay_squared += item['rlc_retx'] ** 2
        rlc_delay_sample += len(bearer.rlc_retx)

    avg_mac_delay = float(mac_delay) / mac_delay_sample if mac_delay_sample > 0 else 0.0
    avg_rlc_delay = float(rlc_delay) / rlc_delay_sample if rlc_delay_sample > 0 else 0.0

    # Calculating variance as a new metric
    mac_variance = (mac_delay_squared / mac_delay_sample - avg_mac_delay**2) if mac_delay_sample > 0 else 0.0
    rlc_variance = (rlc_delay_squared / rlc_delay_sample - avg_rlc_delay**2) if rlc_delay_sample > 0 else 0.0

    print("Average MAC retx delay is: ", avg_mac_delay)
    print("Variance of MAC retx delay is: ", mac_variance)
    print("Average RLC retx delay is:", avg_rlc_delay)
    print("Variance of RLC retx delay is: ", rlc_variance)
