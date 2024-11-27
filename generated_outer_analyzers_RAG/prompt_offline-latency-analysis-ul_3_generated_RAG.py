
#!/usr/bin/python
# Filename: uplink_latency_outer_analyzer.py

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.uplink_latency_analyzer import UplinkLatencyAnalyzer

def uplink_latency_analysis():
    src = OfflineReplayer()
    src.set_input_path('./logs/offline_log_examples/20201115_181637_Xiaomi-Mi10_46000.mi2log')
    
    analyzer = UplinkLatencyAnalyzer()
    analyzer.set_source(src)

    src.run()

    return analyzer

if __name__ == "__main__":
    stats = uplink_latency_analysis()

    total_latency = 0
    total_wait = 0
    total_trans = 0
    total_retx = 8 * stats.cum_err_block[0]

    for latency in stats.all_packets:
        total_wait += latency['Waiting Latency']
        total_trans += latency['Tx Latency']
        total_retx += latency['Retx Latency']

    total_latency = total_wait + total_trans + total_retx
    n = len(stats.all_packets)

    if n > 0:
        print("Average total latency is:", float(total_latency) / n)
        print("Average waiting latency is:", float(total_wait) / n)
        print("Average tx latency is:", float(total_trans) / n)
        print("Average retx latency is:", float(total_retx) / n)
        print("Average total latency excluding retx is:", float(total_wait + total_trans) / n)
    else:
        print("Certain message type(s) missing in the provided log.")
