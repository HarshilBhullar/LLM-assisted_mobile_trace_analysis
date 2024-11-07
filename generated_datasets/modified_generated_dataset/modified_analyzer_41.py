
#!/usr/bin/python
# Filename: modified-msg-statistics-example.py
import os
import sys

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.msg_statistics import MsgStatistics

"""
This example shows how to get modified statistics of a offline log
"""
if __name__ == "__main__":

    # Initialize a 3G/4G monitor
    src = OfflineReplayer()
    src.set_input_path("./offline_log_example.mi2log")

    statistics = MsgStatistics()
    statistics.set_source(src)

    # Start the monitoring
    src.run()

    # Save results with additional metric for unique message types
    f_statistics = open('./msg_type_statistics_extended.txt', 'w')
    for item in statistics.msg_type_statistics:
        unique_msg_count = len(statistics.msg_type_statistics[item])
        f_statistics.write(
            item + " " + str(statistics.msg_type_statistics[item]) + " " + "UniqueCount: " + str(unique_msg_count) + "\n")
    f_statistics.close()

    # Calculate average arrival rate in milliseconds
    f_rate = open('./msg_avg_arrival_rate.txt', 'w')
    for item in statistics.msg_arrival_rate:
        total_intervals = 0
        for k in range(1, len(statistics.msg_arrival_rate[item])):
            interval = (statistics.msg_arrival_rate[item][k] - statistics.msg_arrival_rate[item][k - 1]).total_seconds() * 1000
            total_intervals += interval
        avg_interval = total_intervals / (len(statistics.msg_arrival_rate[item]) - 1) if len(statistics.msg_arrival_rate[item]) > 1 else 0
        f_rate.write(item + " AvgInterval(ms): " + str(avg_interval) + "\n")
    f_rate.close()

    # Calculate and save message length statistics with median
    f_msg_len = open('./msg_length_stats.txt', 'w')
    for item in statistics.msg_lengh:
        lengths = statistics.msg_lengh[item]
        median_length = lengths[len(lengths) // 2] if len(lengths) % 2 != 0 else (lengths[len(lengths) // 2 - 1] + lengths[len(lengths) // 2]) / 2
        f_msg_len.write(item + " Lengths: " + " ".join(map(str, lengths)) + " MedianLength: " + str(median_length) + "\n")
    f_msg_len.close()
