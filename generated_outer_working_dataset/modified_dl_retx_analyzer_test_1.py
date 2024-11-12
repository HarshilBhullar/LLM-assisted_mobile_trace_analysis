
#!/usr/bin/python

import sys

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import LteDlRetxAnalyzer

if __name__ == "__main__":
    src = OfflineReplayer()
    src.set_input_path('./logs/offline_log_examples/20201115_181637_Xiaomi-Mi10_46000.mi2log')

    lteAnalyzer = LteDlRetxAnalyzer()
    lteAnalyzer.set_source(src)

    src.run()

    mac_delay = 0.0
    mac_delay_sample = 0
    
    rlc_delay = 0.0
    rlc_delay_sample = 0

    max_mac_retx = 0
    max_rlc_retx = 0

    for _, bearer in lteAnalyzer.bearer_entity.items():
        for item in bearer.mac_retx:
            mac_delay += item['mac_retx']
            max_mac_retx = max(max_mac_retx, item['mac_retx'])
        mac_delay_sample += len(bearer.mac_retx)

        for item in bearer.rlc_retx:
            rlc_delay += item['rlc_retx']
            max_rlc_retx = max(max_rlc_retx, item['rlc_retx'])
        rlc_delay_sample += len(bearer.rlc_retx)

    avg_mac_delay = float(mac_delay) / mac_delay_sample if mac_delay_sample > 0 else 0.0
    avg_rlc_delay = float(rlc_delay) / rlc_delay_sample if rlc_delay_sample > 0 else 0.0
    
    print("Average MAC retx delay is: ", avg_mac_delay)
    print("Maximum MAC retx delay is: ", max_mac_retx)
    print("Average RLC retx delay is:", avg_rlc_delay)
    print("Maximum RLC retx delay is:", max_rlc_retx)
