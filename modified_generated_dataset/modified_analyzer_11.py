
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
    
    max_mac_delay = 0.0
    max_rlc_delay = 0.0

    for _, bearer in lteAnalyzer.bearer_entity.items():
        for item in bearer.mac_retx:
            mac_delay += item['mac_retx']
            if item['mac_retx'] > max_mac_delay:
                max_mac_delay = item['mac_retx']
        mac_delay_sample += len(bearer.mac_retx)

        for item in bearer.rlc_retx:
            rlc_delay += item['rlc_retx']
            if item['rlc_retx'] > max_rlc_delay:
                max_rlc_delay = item['rlc_retx']
        rlc_delay_sample += len(bearer.rlc_retx)

    avg_mac_delay = float(mac_delay) / mac_delay_sample if mac_delay_sample > 0 else 0.0
    avg_rlc_delay = float(rlc_delay) / rlc_delay_sample if rlc_delay_sample > 0 else 0.0
    
    print("Average MAC retx delay is: ", avg_mac_delay)
    print("Maximum MAC retx delay is: ", max_mac_delay)
    print("Average RLC retx delay is:", avg_rlc_delay)
    print("Maximum RLC retx delay is:", max_rlc_delay)
