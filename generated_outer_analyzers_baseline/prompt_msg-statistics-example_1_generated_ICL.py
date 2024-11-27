
#!/usr/bin/python
# Filename: outer_msg_statistics.py

from mobile_insight.monitor.offline_replayer import OfflineReplayer
from mobile_insight.analyzer.analyzer import MsgStatistics
import os

def calculate_statistics(msg_statistics):
    # Calculate total number of messages and individual message counts
    total_msg_count = sum(msg_statistics.msg_type_statistics.values())
    with open("modified_msg_type_statistics.txt", "w") as f:
        f.write(f"Total number of messages: {total_msg_count}\n")
        for msg_type, count in msg_statistics.msg_type_statistics.items():
            f.write(f"Message Type {msg_type}: {count}\n")

    # Calculate time intervals between consecutive messages for each type
    with open("modified_msg_arrival_rate.txt", "w") as f:
        for msg_type, timestamps in msg_statistics.msg_arrival_rate.items():
            if len(timestamps) > 1:
                intervals = [t2 - t1 for t1, t2 in zip(timestamps[:-1], timestamps[1:])]
                f.write(f"Message Type {msg_type} Intervals: {intervals}\n")

    # Compute the average message length for each type
    with open("modified_msg_length.txt", "w") as f:
        for msg_type, lengths in msg_statistics.msg_lengh.items():
            avg_length = sum(lengths) / len(lengths) if lengths else 0
            f.write(f"Message Type {msg_type} Lengths: {lengths}, Average: {avg_length}\n")

def main():
    # Initialize an OfflineReplayer as the data source
    source = OfflineReplayer()
    source.set_input_path("path/to/log/file")  # Set the path to your log file

    # Create an instance of MsgStatistics and set it as the source for the OfflineReplayer
    msg_statistics = MsgStatistics()
    msg_statistics.set_source(source)

    # Run the OfflineReplayer to process the log data through the MsgStatistics analyzer
    source.run()

    # After processing, calculate and write statistics to files
    calculate_statistics(msg_statistics)

if __name__ == "__main__":
    main()
