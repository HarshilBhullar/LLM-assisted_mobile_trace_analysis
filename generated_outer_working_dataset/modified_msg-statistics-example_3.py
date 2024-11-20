
#!/usr/bin/python
# Filename: modified-msg-statistics-example.py
import os
import sys

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.msg_statistics import MsgStatistics

"""
This modified example shows how to get basic statistics of an offline log
with additional processing on message length statistics.
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
    f_statistics = open('./msg_type_statistics.txt', 'w')
    for item in statistics.msg_type_statistics:
        f_statistics.write(
            item + " " + str(statistics.msg_type_statistics[item]) + "\n")
    f_statistics.close()

    f_rate = open('./msg_arrival_rate.txt', 'w')
    for item in statistics.msg_arrival_rate:
        f_rate.write(item + " ")
        for k in range(1, len(statistics.msg_arrival_rate[item])):
            f_rate.write(str(
                (statistics.msg_arrival_rate[item][k] - statistics.msg_arrival_rate[item][k - 1]).total_seconds() * 1000) + " ")
        f_rate.write("\n")
    f_rate.close()

    # Calculate and save message length statistics with additional processing
    f_msg_len = open('./msg_length_summary.txt', 'w')
    for item in statistics.msg_lengh:
        f_msg_len.write(item + " ")
        total_length = sum(statistics.msg_lengh[item])
        average_length = total_length / len(statistics.msg_lengh[item]) if statistics.msg_lengh[item] else 0
        f_msg_len.write("Total Length: " + str(total_length) + " ")
        f_msg_len.write("Average Length: " + str(average_length) + "\n")
    f_msg_len.close()
