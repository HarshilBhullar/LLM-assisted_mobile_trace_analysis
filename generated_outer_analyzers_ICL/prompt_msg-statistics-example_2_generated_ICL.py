
#!/usr/bin/python
# Filename: modified-msg-statistics-analysis.py
import os
import sys

"""
Offline analysis by replaying logs and computing message statistics
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgStatistics

if __name__ == "__main__":

    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./offline_log_example.mi2log")

    # Initialize the MsgStatistics analyzer
    msg_statistics = MsgStatistics()
    msg_statistics.set_source(src)

    # Start the monitoring
    src.run()

    # Process and save the message statistics
    total_messages = sum(msg_statistics.msg_type_statistics.values())
    with open("modified_msg_type_statistics.txt", "w") as f:
        for msg_type, count in msg_statistics.msg_type_statistics.items():
            percentage = (count / total_messages) * 100
            f.write(f"{msg_type}: {count} messages, {percentage:.2f}%\n")

    # Calculate and save the message arrival intervals
    with open("modified_msg_arrival_rate.txt", "w") as f:
        for msg_type, timestamps in msg_statistics.msg_arrival_rate.items():
            intervals = [
                (timestamps[i] - timestamps[i - 1]) * 1000
                for i in range(1, len(timestamps))
            ]
            f.write(f"{msg_type}: {intervals}\n")

    # Record and save the message lengths
    with open("modified_msg_length.txt", "w") as f:
        for msg_type, lengths in msg_statistics.msg_lengh.items():
            average_length = sum(lengths) / len(lengths) if lengths else 0
            f.write(f"{msg_type}: {lengths}, Average length: {average_length:.2f}\n")
