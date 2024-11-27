
#!/usr/bin/python
# Filename: modified-offline-analysis-example.py
import os
import sys

"""
Offline analysis by replaying logs with message statistics
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgStatistics

if __name__ == "__main__":

    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")
    # src.enable_log_all()

    msg_statistics = MsgStatistics()
    msg_statistics.set_source(src)

    # Start the monitoring
    src.run()

    # Calculate and write message type statistics
    with open('./modified_msg_type_statistics.txt', 'w') as f_statistics:
        total_messages = sum(msg_statistics.msg_type_statistics.values())
        f_statistics.write(f"Total messages: {total_messages}\n")
        for item, count in msg_statistics.msg_type_statistics.items():
            f_statistics.write(f"{item}: {count}\n")

    # Calculate and write arrival rate statistics
    with open('./modified_msg_arrival_rate.txt', 'w') as f_arrival_rate:
        for msg_type, timestamps in msg_statistics.msg_arrival_rate.items():
            intervals = [t2 - t1 for t1, t2 in zip(timestamps, timestamps[1:])]
            f_arrival_rate.write(f"{msg_type} intervals: {intervals}\n")

    # Calculate and write message length statistics
    with open('./modified_msg_length.txt', 'w') as f_length:
        for msg_type, lengths in msg_statistics.msg_lengh.items():
            avg_length = sum(lengths) / len(lengths) if lengths else 0
            f_length.write(f"{msg_type} lengths: {lengths}, average: {avg_length}\n")
