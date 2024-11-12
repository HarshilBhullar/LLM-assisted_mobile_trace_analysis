
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

    # Save results
    f_statistics = open('./modified_msg_type_statistics.txt', 'w')
    for item in statistics.msg_type_statistics:
        f_statistics.write(
            item + " " + str(statistics.msg_type_statistics[item]) + "\n")
    f_statistics.close()

    f_rate = open('./modified_msg_arrival_rate.txt', 'w')
    for item in statistics.msg_arrival_rate:
        f_rate.write(item + " ")
        for k in range(1, len(statistics.msg_arrival_rate[item])):
            interval = (statistics.msg_arrival_rate[item][k] - statistics.msg_arrival_rate[item][k - 1]).total_seconds() * 1000
            f_rate.write(str(interval) + " ")
        # Writing average arrival rate for each message type
        if len(statistics.msg_arrival_rate[item]) > 1:
            total_intervals = len(statistics.msg_arrival_rate[item]) - 1
            total_time = sum(
                (statistics.msg_arrival_rate[item][k] - statistics.msg_arrival_rate[item][k - 1]).total_seconds() * 1000
                for k in range(1, len(statistics.msg_arrival_rate[item]))
            )
            avg_interval = total_time / total_intervals if total_intervals != 0 else 0
            f_rate.write("Average: " + str(avg_interval) + " ms")
        f_rate.write("\n")
    f_rate.close()

    f_msg_len = open('./modified_msg_length.txt', 'w')
    for item in statistics.msg_lengh:
        f_msg_len.write(item + " ")
        for k in range(0, len(statistics.msg_lengh[item])):
            f_msg_len.write(str(statistics.msg_lengh[item][k]) + " ")
        # Writing average message length for each message type
        avg_length = sum(statistics.msg_lengh[item]) / len(statistics.msg_lengh[item]) if len(statistics.msg_lengh[item]) > 0 else 0
        f_msg_len.write("Average Length: " + str(avg_length))
        f_msg_len.write("\n")
    f_msg_len.close()
