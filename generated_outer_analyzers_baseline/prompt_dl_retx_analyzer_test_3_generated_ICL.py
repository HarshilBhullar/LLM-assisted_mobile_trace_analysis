
#!/usr/bin/env python3

from mobile_insight.monitor import OfflineReplayer
from lte_dl_retx_analyzer import LteDlRetxAnalyzer

def main(log_file_path):
    # Initialize the offline replayer
    src = OfflineReplayer()
    src.set_input_path(log_file_path)

    # Initialize the analyzer and set the data source
    analyzer = LteDlRetxAnalyzer()
    analyzer.set_source(src)

    # Run the analysis
    src.run()

    # Variables to calculate total and maximum delays
    total_mac_retx_delay = 0
    total_rlc_retx_delay = 0
    max_mac_retx_delay = 0
    max_rlc_retx_delay = 0
    mac_retx_samples = 0
    rlc_retx_samples = 0

    # Iterate over each bearer and accumulate metrics
    for bearer in analyzer.bearer_entity.values():
        # Process MAC retransmission delays
        for mac_retx in bearer.mac_retx:
            delay = mac_retx['mac_retx']
            total_mac_retx_delay += delay
            mac_retx_samples += 1
            if delay > max_mac_retx_delay:
                max_mac_retx_delay = delay

        # Process RLC retransmission delays
        for rlc_retx in bearer.rlc_retx:
            delay = rlc_retx['rlc_retx']
            total_rlc_retx_delay += delay
            rlc_retx_samples += 1
            if delay > max_rlc_retx_delay:
                max_rlc_retx_delay = delay

    # Calculate average delays
    avg_mac_retx_delay = total_mac_retx_delay / mac_retx_samples if mac_retx_samples > 0 else 0
    avg_rlc_retx_delay = total_rlc_retx_delay / rlc_retx_samples if rlc_retx_samples > 0 else 0

    # Output results
    print("MAC Retransmission Delay: Average = {:.2f}, Maximum = {}".format(avg_mac_retx_delay, max_mac_retx_delay))
    print("RLC Retransmission Delay: Average = {:.2f}, Maximum = {}".format(avg_rlc_retx_delay, max_rlc_retx_delay))

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: {} <log_file_path>".format(sys.argv[0]))
        sys.exit(1)

    log_file_path = sys.argv[1]
    main(log_file_path)
