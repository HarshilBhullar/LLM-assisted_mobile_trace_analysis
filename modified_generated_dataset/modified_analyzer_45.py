
#!/usr/bin/python
# Filename: modified-msg-statistics-example.py
import os
import sys

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.msg_statistics import MsgStatistics

"""
This example shows how to get enhanced statistics of an offline log
"""
if __name__ == "__main__":

    # Initialize a 3G/4G monitor
    src = OfflineReplayer()
    src.set_input_path("./offline_log_example.mi2log")

    statistics = MsgStatistics()
    statistics.set_source(src)

    # Start the monitoring
    src.run()

    # Save results with additional metrics
    f_statistics = open('./enhanced_msg_type_statistics.txt', 'w')
    for item in statistics.msg_type_statistics:
        # Including percentage of each message type
        total_msgs = sum(statistics.msg_type_statistics.values())
        percentage = (statistics.msg_type_statistics[item] / total_msgs) * 100
        f_statistics.write(
            item + " " + str(statistics.msg_type_statistics[item]) + " (" + str(percentage) + "%)\n")
    f_statistics.close()

    f_rate = open('./enhanced_msg_arrival_rate.txt', 'w')
    for item in statistics.msg_arrival_rate:
        f_rate.write(item + " ")
        for k in range(1, len(statistics.msg_arrival_rate[item])):
            interval_ms = (statistics.msg_arrival_rate[item][k] - statistics.msg_arrival_rate[item][k - 1]).total_seconds() * 1000
            # Include variance of arrival intervals
            variance = interval_ms ** 2
            f_rate.write(str(interval_ms) + " " + str(variance) + " ")
        f_rate.write("\n")
    f_rate.close()

    f_msg_len = open('./enhanced_msg_length.txt', 'w')
    for item in statistics.msg_lengh:
        f_msg_len.write(item + " ")
        max_len = max(statistics.msg_lengh[item]) if statistics.msg_lengh[item] else 0
        min_len = min(statistics.msg_lengh[item]) if statistics.msg_lengh[item] else 0
        avg_len = sum(statistics.msg_lengh[item]) / len(statistics.msg_lengh[item]) if statistics.msg_lengh[item] else 0
        f_msg_len.write("Max: " + str(max_len) + " Min: " + str(min_len) + " Avg: " + str(avg_len) + " ")
        f_msg_len.write("\n")
    f_msg_len.close()
