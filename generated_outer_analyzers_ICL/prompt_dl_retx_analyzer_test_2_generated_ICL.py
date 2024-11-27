
#!/usr/bin/python
# Filename: modified-offline-analysis-example.py
import os
import sys

"""
Modified offline analysis by replaying logs
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import LteDlRetxAnalyzer

def my_analysis(log_path):
    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path(log_path)

    lte_dl_retx_analyzer = LteDlRetxAnalyzer()
    lte_dl_retx_analyzer.set_source(src)

    # Start the monitoring
    try:
        src.run()

        for rb_entity in lte_dl_retx_analyzer.bearer_entity.values():
            mac_retx_delays = [entry['mac_retx'] for entry in rb_entity.mac_retx]
            rlc_retx_delays = [entry['rlc_retx'] for entry in rb_entity.rlc_retx]

            if mac_retx_delays:
                avg_mac_retx = sum(mac_retx_delays) / len(mac_retx_delays)
                max_mac_retx = max(mac_retx_delays)
                print(f"RB {rb_entity}: Average MAC Retransmission Delay: {avg_mac_retx}, Max: {max_mac_retx}")
            else:
                print(f"RB {rb_entity}: No MAC retransmission data available.")

            if rlc_retx_delays:
                avg_rlc_retx = sum(rlc_retx_delays) / len(rlc_retx_delays)
                max_rlc_retx = max(rlc_retx_delays)
                print(f"RB {rb_entity}: Average RLC Retransmission Delay: {avg_rlc_retx}, Max: {max_rlc_retx}")
            else:
                print(f"RB {rb_entity}: No RLC retransmission data available.")

    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python modified-offline-analysis-example.py <path_to_log>")
        sys.exit(1)

    log_path = sys.argv[1]
    if not os.path.exists(log_path):
        print(f"Log path {log_path} does not exist.")
        sys.exit(1)

    my_analysis(log_path)
