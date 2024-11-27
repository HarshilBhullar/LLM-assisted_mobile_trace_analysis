
#!/usr/bin/python3
# Filename: uplink_latency_evaluator.py

from mobile_insight.monitor import OfflineReplayer
from uplink_latency_analyzer import UplinkLatencyAnalyzer

def calculate_latencies(uplink_analyzer):
    total_waiting_latency = 0
    total_tx_latency = 0
    total_retx_latency = 0

    all_packets = uplink_analyzer.all_packets

    for packet in all_packets:
        total_waiting_latency += packet['Waiting Latency']
        total_tx_latency += packet['Tx Latency']
        total_retx_latency += packet['Retx Latency']

    total_latency = total_waiting_latency + total_tx_latency + total_retx_latency
    num_packets = len(all_packets)

    if num_packets > 0:
        avg_waiting_latency = total_waiting_latency / num_packets
        avg_tx_latency = total_tx_latency / num_packets
        avg_retx_latency = total_retx_latency / num_packets
        avg_total_latency = total_latency / num_packets
    else:
        avg_waiting_latency = avg_tx_latency = avg_retx_latency = avg_total_latency = 0

    print(f"Average Waiting Latency: {avg_waiting_latency:.2f} ms")
    print(f"Average Transmission Latency: {avg_tx_latency:.2f} ms")
    print(f"Average Retransmission Latency: {avg_retx_latency:.2f} ms")
    print(f"Average Total Latency: {avg_total_latency:.2f} ms")

    weights = {'waiting': 0.5, 'tx': 0.3, 'retx': 0.2}
    weighted_avg_latency = (avg_waiting_latency * weights['waiting'] +
                            avg_tx_latency * weights['tx'] +
                            avg_retx_latency * weights['retx'])
    print(f"Weighted Average Latency: {weighted_avg_latency:.2f} ms")


if __name__ == "__main__":
    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/uplink_latency_trace.mi2log")

    uplink_analyzer = UplinkLatencyAnalyzer()
    uplink_analyzer.set_source(src)

    # Start the monitoring
    src.run()

    # Calculate and print latency statistics
    calculate_latencies(uplink_analyzer)
