
#!/usr/bin/python
# Filename: modified-msg-statistics-example.py
import os
import sys

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.msg_statistics import MsgStatistics

"""
This modified example shows how to get extended statistics of an offline log
"""
if __name__ == "__main__":

    # Initialize a 3G/4G monitor
    src = OfflineReplayer()
    src.set_input_path("./offline_log_example.mi2log")

    statistics = MsgStatistics()
    statistics.set_source(src)

    # Start the monitoring
    src.run()

    # Save message type statistics
    with open('./modified_msg_type_statistics.txt', 'w') as f_statistics:
        for item in statistics.msg_type_statistics:
            f_statistics.write(
                f"{item} {statistics.msg_type_statistics[item]}\n")

    # Calculate and save average arrival rate in milliseconds
    with open('./average_msg_arrival_rate.txt', 'w') as f_avg_rate:
        for item in statistics.msg_arrival_rate:
            intervals = [
                (statistics.msg_arrival_rate[item][k] - statistics.msg_arrival_rate[item][k - 1]).total_seconds() * 1000
                for k in range(1, len(statistics.msg_arrival_rate[item]))
            ]
            if intervals:
                avg_interval = sum(intervals) / len(intervals)
                f_avg_rate.write(f"{item} {avg_interval}\n")

    # Save message length statistics with a cumulative length
    with open('./cumulative_msg_length.txt', 'w') as f_cum_len:
        for item in statistics.msg_lengh:
            cumulative_length = sum(statistics.msg_lengh[item])
            f_cum_len.write(f"{item} Total Length: {cumulative_length} Details: ")
            for length in statistics.msg_lengh[item]:
                f_cum_len.write(f"{length} ")
            f_cum_len.write("\n")
