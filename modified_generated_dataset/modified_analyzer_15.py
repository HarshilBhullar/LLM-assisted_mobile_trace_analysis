
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

    mac_delay_squared_sum = 0.0
    mac_delay_sample = 0
    
    rlc_delay_squared_sum = 0.0
    rlc_delay_sample = 0

    for _, bearer in lteAnalyzer.bearer_entity.items():
        for item in bearer.mac_retx:
            mac_delay_squared_sum += item['mac_retx'] ** 2
        mac_delay_sample += len(bearer.mac_retx)

        for item in bearer.rlc_retx:
            rlc_delay_squared_sum += item['rlc_retx'] ** 2
        rlc_delay_sample += len(bearer.rlc_retx)

    avg_mac_delay_squared = float(mac_delay_squared_sum) / mac_delay_sample if mac_delay_sample > 0 else 0.0
    avg_rlc_delay_squared = float(rlc_delay_squared_sum) / rlc_delay_sample if rlc_delay_sample > 0 else 0.0
    
    print("Average squared MAC retx delay is: ", avg_mac_delay_squared)
    print("Average squared RLC retx delay is:", avg_rlc_delay_squared)
