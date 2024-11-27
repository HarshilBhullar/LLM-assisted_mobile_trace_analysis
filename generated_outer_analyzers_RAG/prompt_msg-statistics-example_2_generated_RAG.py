
#!/usr/bin/python
# Filename: modified_msg_statistics.py

import os
import sys
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgStatistics

def calculate_intervals(timestamps):
    intervals = []
    for i in range(1, len(timestamps)):
        interval = (timestamps[i] - timestamps[i - 1]).total_seconds() * 1000  # convert to milliseconds
        intervals.append(interval)
    return intervals

if __name__ == "__main__":
    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./offline_log_example.mi2log")

    statistics = MsgStatistics()
    statistics.set_source(src)

    # Start the monitoring
    src.run()

    # Total number of messages
    total_messages = sum(statistics.msg_type_statistics.values())

    # Save results
    with open('./modified_msg_type_statistics.txt', 'w') as f_statistics:
        for item in statistics.msg_type_statistics:
            percentage = (statistics.msg_type_statistics[item] / total_messages) * 100
            f_statistics.write(f"{item} {statistics.msg_type_statistics[item]} ({percentage:.2f}%)\n")

    with open('./modified_msg_arrival_rate.txt', 'w') as f_arrival:
        for item in statistics.msg_arrival_rate:
            if len(statistics.msg_arrival_rate[item]) > 1:
                intervals = calculate_intervals(statistics.msg_arrival_rate[item])
                f_arrival.write(f"{item} {intervals}\n")

    with open('./modified_msg_length.txt', 'w') as f_length:
        for item in statistics.msg_lengh:
            avg_length = sum(statistics.msg_lengh[item]) / len(statistics.msg_lengh[item])
            f_length.write(f"{item} {statistics.msg_lengh[item]} (avg: {avg_length:.2f})\n")
