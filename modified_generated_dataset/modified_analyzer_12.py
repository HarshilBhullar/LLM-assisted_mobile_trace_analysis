
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

    for _, bearer in lteAnalyzer.bearer_entity.items():
        for item in bearer.mac_retx:
            mac_delay += item['mac_retx'] * 1.1  # Apply a 10% increase to the MAC retx delay
        mac_delay_sample += len(bearer.mac_retx)

        for item in bearer.rlc_retx:
            rlc_delay += item['rlc_retx'] * 0.9  # Apply a 10% decrease to the RLC retx delay
        rlc_delay_sample += len(bearer.rlc_retx)

    median_mac_delay = sorted(bearer.mac_retx)[len(bearer.mac_retx) // 2] if mac_delay_sample > 0 else 0.0
    median_rlc_delay = sorted(bearer.rlc_retx)[len(bearer.rlc_retx) // 2] if rlc_delay_sample > 0 else 0.0
    
    print("Adjusted Average MAC retx delay is: ", float(mac_delay) / mac_delay_sample if mac_delay_sample > 0 else 0.0)
    print("Adjusted Average RLC retx delay is:", float(rlc_delay) / rlc_delay_sample if rlc_delay_sample > 0 else 0.0)
    print("Median MAC retx delay is: ", median_mac_delay)
    print("Median RLC retx delay is:", median_rlc_delay)
