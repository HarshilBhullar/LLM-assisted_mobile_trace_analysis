
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
    for item in statistics.msg_type_statistics:
        # Here we normalize the statistics by dividing by the total number of messages
        total_msgs = sum(statistics.msg_type_statistics.values())
        normalized_value = statistics.msg_type_statistics[item] / total_msgs if total_msgs > 0 else 0
        f_statistics.write(item + " " + str(normalized_value) + "\n")
    f_statistics.close()

    f_rate = open('./modified_msg_arrival_rate.txt', 'w')
    for item in statistics.msg_arrival_rate:
        f_rate.write(item + " ")
        # Calculate the average arrival rate instead of the difference between timestamps
        if len(statistics.msg_arrival_rate[item]) > 1:
            total_time = (statistics.msg_arrival_rate[item][-1] - statistics.msg_arrival_rate[item][0]).total_seconds()
            average_rate = total_time / (len(statistics.msg_arrival_rate[item]) - 1) * 1000  # in milliseconds
            f_rate.write(str(average_rate) + " ")
        f_rate.write("\n")
    f_rate.close()

    f_msg_len = open('./modified_msg_length.txt', 'w')
    for item in statistics.msg_lengh:
        f_msg_len.write(item + " ")
        # Calculate and write the median message length instead of listing all lengths
        if statistics.msg_lengh[item]:
            sorted_lengths = sorted(statistics.msg_lengh[item])
            mid = len(sorted_lengths) // 2
            median_length = (sorted_lengths[mid] if len(sorted_lengths) % 2 == 1 else 
                             (sorted_lengths[mid - 1] + sorted_lengths[mid]) / 2)
            f_msg_len.write(str(median_length) + " ")
        f_msg_len.write("\n")
    f_msg_len.close()
