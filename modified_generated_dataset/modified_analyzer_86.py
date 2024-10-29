
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

    # Added new metric calculations
    total_mac_retx_events = 0
    total_rlc_retx_events = 0

    for _, bearer in lteAnalyzer.bearer_entity.items():
        for item in bearer.mac_retx:
            mac_delay += item['mac_retx']
        mac_delay_sample += len(bearer.mac_retx)
        total_mac_retx_events += len(bearer.mac_retx)  # Count total MAC retx events

        for item in bearer.rlc_retx:
            rlc_delay += item['rlc_retx']
        rlc_delay_sample += len(bearer.rlc_retx)
        total_rlc_retx_events += len(bearer.rlc_retx)  # Count total RLC retx events

    avg_mac_delay = float(mac_delay) / mac_delay_sample if mac_delay_sample > 0 else 0.0
    avg_rlc_delay = float(rlc_delay) / rlc_delay_sample if rlc_delay_sample > 0 else 0.0

    # Calculate average number of retx events
    avg_mac_retx_events = total_mac_retx_events / len(lteAnalyzer.bearer_entity) if len(lteAnalyzer.bearer_entity) > 0 else 0
    avg_rlc_retx_events = total_rlc_retx_events / len(lteAnalyzer.bearer_entity) if len(lteAnalyzer.bearer_entity) > 0 else 0

    print("Average MAC retx delay is: ", avg_mac_delay)
    print("Average RLC retx delay is:", avg_rlc_delay)
    print("Average MAC retx events per bearer: ", avg_mac_retx_events)
    print("Average RLC retx events per bearer: ", avg_rlc_retx_events)
