
#!/usr/bin/python
# Filename: offline-analysis-msg-statistics.py
import os
import sys

"""
Offline analysis by replaying logs to calculate message statistics
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgStatistics

if __name__ == "__main__":

    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")
    src.enable_log_all()

    msg_statistics = MsgStatistics()
    msg_statistics.set_source(src)

    # Run the offline analysis
    src.run()

    # Calculate and write statistics
    with open("./modified_msg_type_statistics.txt", "w") as type_file:
        total_msgs = sum(msg_statistics.msg_type_statistics.values())
        type_file.write(f"Total messages: {total_msgs}\n")
        for msg_type, count in msg_statistics.msg_type_statistics.items():
            type_file.write(f"Message Type {msg_type}: {count}\n")

    with open("./modified_msg_arrival_rate.txt", "w") as arrival_file:
        for msg_type, timestamps in msg_statistics.msg_arrival_rate.items():
            if len(timestamps) > 1:
                intervals = [t2 - t1 for t1, t2 in zip(timestamps, timestamps[1:])]
                arrival_file.write(f"Message Type {msg_type} Intervals: {intervals}\n")
            else:
                arrival_file.write(f"Message Type {msg_type} has insufficient data for interval calculation.\n")

    with open("./modified_msg_length.txt", "w") as length_file:
        for msg_type, lengths in msg_statistics.msg_lengh.items():
            avg_length = sum(lengths) / len(lengths) if lengths else 0
            length_file.write(f"Message Type {msg_type} Average Length: {avg_length}\n")
            length_file.write(f"Message Type {msg_type} Lengths: {lengths}\n")
