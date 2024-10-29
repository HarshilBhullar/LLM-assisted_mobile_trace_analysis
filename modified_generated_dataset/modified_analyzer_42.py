
#!/usr/bin/python
# Filename: modified-msg-statistics-example.py
import os
import sys

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.msg_statistics import MsgStatistics

"""
This example shows how to get advanced statistics of an offline log
"""
if __name__ == "__main__":

    # Initialize a 3G/4G monitor
    src = OfflineReplayer()
    src.set_input_path("./offline_log_example.mi2log")

    statistics = MsgStatistics()
    statistics.set_source(src)

    # Start the monitoring
    src.run()

    # Save results with additional processing
    f_statistics = open('./enhanced_msg_type_statistics.txt', 'w')
    for item in statistics.msg_type_statistics:
        # Save the percentage of each message type
        total_messages = sum(statistics.msg_type_statistics.values())
        percentage = (statistics.msg_type_statistics[item] / total_messages) * 100
        f_statistics.write(
            item + " " + str(statistics.msg_type_statistics[item]) + " (" + f"{percentage:.2f}" + "%)\n")
    f_statistics.close()

    f_rate = open('./enhanced_msg_arrival_rate.txt', 'w')
    for item in statistics.msg_arrival_rate:
        f_rate.write(item + " ")
        if len(statistics.msg_arrival_rate[item]) > 1:
            # Calculate the average time interval between messages
            intervals = [(statistics.msg_arrival_rate[item][k] - statistics.msg_arrival_rate[item][k - 1]).total_seconds() * 1000
                         for k in range(1, len(statistics.msg_arrival_rate[item]))]
            average_interval = sum(intervals) / len(intervals)
            f_rate.write("Average Interval: " + f"{average_interval:.2f}" + " ms ")
        else:
            f_rate.write("Insufficient data for interval calculation ")
        f_rate.write("\n")
    f_rate.close()

    f_msg_len = open('./enhanced_msg_length.txt', 'w')
    for item in statistics.msg_lengh:
        f_msg_len.write(item + " ")
        # Calculate the variance of message lengths
        if len(statistics.msg_lengh[item]) > 1:
            mean_length = sum(statistics.msg_lengh[item]) / len(statistics.msg_lengh[item])
            variance = sum((x - mean_length) ** 2 for x in statistics.msg_lengh[item]) / len(statistics.msg_lengh[item])
            f_msg_len.write("Variance: " + f"{variance:.2f} ")
        else:
            f_msg_len.write("Insufficient data for variance calculation ")
        f_msg_len.write("\n")
    f_msg_len.close()
