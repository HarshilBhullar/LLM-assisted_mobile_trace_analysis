
#!/usr/bin/python
# Filename: modified-msg-statistics-example.py
import os
import sys

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.msg_statistics import MsgStatistics

"""
This example shows how to get modified statistics of an offline log
"""
if __name__ == "__main__":

    # Initialize a 3G/4G monitor
    src = OfflineReplayer()
    src.set_input_path("./offline_log_example.mi2log")

    statistics = MsgStatistics()
    statistics.set_source(src)

    # Start the monitoring
    src.run()

    # Save results
    f_statistics = open('./modified_msg_type_statistics.txt', 'w')
    total_messages = sum(statistics.msg_type_statistics.values())
    for item in statistics.msg_type_statistics:
        percentage = (statistics.msg_type_statistics[item] / total_messages) * 100
        f_statistics.write(
            item + " " + str(statistics.msg_type_statistics[item]) + " (" + str(percentage) + "%)\n")
    f_statistics.close()

    f_rate = open('./modified_msg_arrival_rate.txt', 'w')
    for item in statistics.msg_arrival_rate:
        f_rate.write(item + " ")
        for k in range(1, len(statistics.msg_arrival_rate[item])):
            interval = (statistics.msg_arrival_rate[item][k] - statistics.msg_arrival_rate[item][k - 1]).total_seconds() * 1000
            f_rate.write(str(interval) + " ")
        f_rate.write("\n")
    f_rate.close()

    f_msg_len = open('./modified_msg_length.txt', 'w')
    for item in statistics.msg_lengh:
        f_msg_len.write(item + " ")
        average_length = sum(statistics.msg_lengh[item]) / len(statistics.msg_lengh[item])
        for k in range(0, len(statistics.msg_lengh[item])):
            f_msg_len.write(str(statistics.msg_lengh[item][k]) + " ")
        f_msg_len.write("Average: " + str(average_length) + "\n")
    f_msg_len.close()
