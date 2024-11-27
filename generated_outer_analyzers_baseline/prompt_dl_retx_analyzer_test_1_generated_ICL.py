
#!/usr/bin/python
# Filename: lte_dl_retx_analyzer_outer.py

"""
Function: Execute downlink MAC retransmission delay and RLC retransmission delay analysis
Author: Qianru Li
"""

from mobile_insight.monitor import OfflineReplayer
from lte_dl_retx_analyzer import LteDlRetxAnalyzer

def my_analysis(log_path):
    # Initialize the offline replayer
    src = OfflineReplayer()
    src.set_input_path(log_path)

    # Initialize the analyzer
    analyzer = LteDlRetxAnalyzer()
    analyzer.set_source(src)

    # Run the source to process the logs
    try:
        src.run()
    except Exception as e:
        print(f"An error occurred during log processing: {e}")
        return
    
    # Calculate and print analysis results
    for cfg_idx, bearer in analyzer.bearer_entity.items():
        mac_retx_delays = [entry['mac_retx'] for entry in bearer.mac_retx]
        rlc_retx_delays = [entry['rlc_retx'] for entry in bearer.rlc_retx]

        if mac_retx_delays:
            avg_mac_retx_delay = sum(mac_retx_delays) / len(mac_retx_delays)
            max_mac_retx_delay = max(mac_retx_delays)
            print(f"Bearer {cfg_idx}: Average MAC Retransmission Delay: {avg_mac_retx_delay}, Maximum MAC Retransmission Delay: {max_mac_retx_delay}")
        else:
            print(f"Bearer {cfg_idx}: No MAC Retransmissions Detected")

        if rlc_retx_delays:
            avg_rlc_retx_delay = sum(rlc_retx_delays) / len(rlc_retx_delays)
            max_rlc_retx_delay = max(rlc_retx_delays)
            print(f"Bearer {cfg_idx}: Average RLC Retransmission Delay: {avg_rlc_retx_delay}, Maximum RLC Retransmission Delay: {max_rlc_retx_delay}")
        else:
            print(f"Bearer {cfg_idx}: No RLC Retransmissions Detected")

if __name__ == "__main__":
    # Example log path; replace with the actual path to the log file
    log_path = "path/to/your/log_file.mi2log"
    my_analysis(log_path)
