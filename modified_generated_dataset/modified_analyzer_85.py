
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
        # Modified to calculate the sum of squares of MAC retx delays
        for item in bearer.mac_retx:
            mac_delay += item['mac_retx'] ** 2
        mac_delay_sample += len(bearer.mac_retx)

        # Modified to calculate the sum of squares of RLC retx delays
        for item in bearer.rlc_retx:
            rlc_delay += item['rlc_retx'] ** 2
        rlc_delay_sample += len(bearer.rlc_retx)

    # Modified to calculate the root mean square (RMS) instead of the average
    rms_mac_delay = (mac_delay / mac_delay_sample) ** 0.5 if mac_delay_sample > 0 else 0.0
    rms_rlc_delay = (rlc_delay / rlc_delay_sample) ** 0.5 if rlc_delay_sample > 0 else 0.0
    
    print("RMS MAC retx delay is: ", rms_mac_delay)
    print("RMS RLC retx delay is:", rms_rlc_delay)
