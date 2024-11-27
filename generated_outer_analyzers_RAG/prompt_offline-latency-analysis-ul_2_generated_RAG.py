
#!/usr/bin/python
# Filename: uplink_latency_analysis.py

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import UplinkLatencyAnalyzer

def uplink_latency_analysis():
    # Set up the OfflineReplayer as the data source
    src = OfflineReplayer()
    src.set_input_path('./path/to/your/logfile.mi2log')

    # Instantiate the UplinkLatencyAnalyzer
    analyzer = UplinkLatencyAnalyzer()
    analyzer.set_source(src)

    # Run the analysis
    src.run()

    return analyzer

if __name__ == "__main__":
    # Perform the analysis
    stats = uplink_latency_analysis()

    # Retrieve data from the analyzer
    total_wait = sum(pkt['Waiting Latency'] for pkt in stats.all_packets)
    total_trans = sum(pkt['Tx Latency'] for pkt in stats.all_packets)
    total_retx = sum(pkt['Retx Latency'] for pkt in stats.all_packets) + 8 * stats.cum_err_block[0]
    total_latency = total_wait + total_trans + total_retx

    n = len(stats.all_packets)

    # Check if packets were processed
    if n > 0:
        avg_latency = float(total_latency) / n
        avg_wait = float(total_wait) / n
        avg_trans = float(total_trans) / n
        avg_retx = float(total_retx) / n

        # Output calculated average latencies
        print("Average latency is:", avg_latency)
        print("Average waiting latency is:", avg_wait)
        print("Average tx latency is:", avg_trans)
        print("Average retx latency is:", avg_retx)

        # Weighted average latency calculation
        weights = {'wait': 0.5, 'trans': 0.3, 'retx': 0.2}
        weighted_avg_latency = (weights['wait'] * avg_wait +
                                weights['trans'] * avg_trans +
                                weights['retx'] * avg_retx)
        print("Weighted average latency is:", weighted_avg_latency)
    else:
        print("Certain message type(s) missing in the provided log.")
