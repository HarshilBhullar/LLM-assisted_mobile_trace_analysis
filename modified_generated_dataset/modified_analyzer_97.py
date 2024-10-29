
#!/usr/bin/python
# Filename: modified-msg-statistics-example.py
import os
import sys

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.msg_statistics import MsgStatistics

"""
This modified example shows how to get enhanced statistics of an offline log, 
including additional metrics like average message length and time variance.
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
    f_statistics = open('./modified_msg_type_statistics.txt', 'w')
    for item in statistics.msg_type_statistics:
        f_statistics.write(
            item + " " + str(statistics.msg_type_statistics[item]) + "\n")
    f_statistics.close()

    # Calculate and save average message arrival time and variance
    f_rate = open('./modified_msg_arrival_rate.txt', 'w')
    for item in statistics.msg_arrival_rate:
        time_diffs = []
        for k in range(1, len(statistics.msg_arrival_rate[item])):
            time_diff = (statistics.msg_arrival_rate[item][k] - statistics.msg_arrival_rate[item][k - 1]).total_seconds() * 1000
            time_diffs.append(time_diff)
            f_rate.write(str(time_diff) + " ")
        
        if time_diffs:
            average_time_diff = sum(time_diffs) / len(time_diffs)
            variance_time_diff = sum((x - average_time_diff) ** 2 for x in time_diffs) / len(time_diffs)
            f_rate.write("Average: " + str(average_time_diff) + " Variance: " + str(variance_time_diff))
        
        f_rate.write("\n")
    f_rate.close()

    # Calculate and save message lengths and average length
    f_msg_len = open('./modified_msg_length.txt', 'w')
    for item in statistics.msg_lengh:
        total_length = sum(statistics.msg_lengh[item])
        num_msgs = len(statistics.msg_lengh[item])
        average_length = total_length / num_msgs if num_msgs > 0 else 0

        f_msg_len.write(item + " ")
        for length in statistics.msg_lengh[item]:
            f_msg_len.write(str(length) + " ")
        
        f_msg_len.write("Average Length: " + str(average_length) + "\n")
    f_msg_len.close()
