
#!/usr/bin/python
# Filename: outer_lte_dl_retx_analyzer.py

"""
Function: Utilize LteDlRetxAnalyzer to evaluate and output metrics related to downlink MAC and RLC retransmissions
Author: Qianru Li
"""

from mobile_insight.monitor.offline_replayer import OfflineReplayer
from mobile_insight.analyzer.analyzer import MsgLogger
from lte_dl_retx_analyzer import LteDlRetxAnalyzer

def calculate_enhanced_metric(analyzer):
    for cfg_idx, entity in analyzer.bearer_entity.items():
        total_mac_retx = len(entity.mac_retx)
        total_rlc_retx = len(entity.rlc_retx)
        print(f"Bearer {cfg_idx}: Total MAC Retransmissions = {total_mac_retx}, Total RLC Retransmissions = {total_rlc_retx}")

def main():
    # Create an offline replayer to replay logs from a specified directory
    src = OfflineReplayer()
    src.set_input_path("/path/to/log/directory")  # Update with the path to your log directory

    # Initialize and configure a MsgLogger
    msg_logger = MsgLogger()
    msg_logger.set_source(src)
    msg_logger.set_decode_format(MsgLogger.JSON)

    # Initialize the LteDlRetxAnalyzer
    dl_retx_analyzer = LteDlRetxAnalyzer()
    dl_retx_analyzer.set_source(src)

    # Run the monitoring
    src.run()

    # Calculate and print enhanced metrics after log replay
    calculate_enhanced_metric(dl_retx_analyzer)

if __name__ == "__main__":
    main()
