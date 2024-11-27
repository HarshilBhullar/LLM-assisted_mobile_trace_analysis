
#!/usr/bin/python
# Filename: outer_analyzer.py

import os
from mobile_insight.monitor import OfflineReplayer
from msg_statistics import MsgStatistics

def main():
    # Setup and Initialization
    log_path = "./offline_log_example.mi2log"
    if not os.path.exists(log_path):
        raise FileNotFoundError(f"Log file not found: {log_path}")

    # Initialize the OfflineReplayer
    src = OfflineReplayer()
    src.set_input_path(log_path)

    # Initialize the MsgStatistics Analyzer
    msg_stats = MsgStatistics()
    msg_stats.set_source(src)

    # Execution of Analysis
    src.run()

    # Data Processing and Output
    with open("modified_msg_type_statistics.txt", "w") as f_type_stats:
        total_msgs = sum(msg_stats.msg_type_statistics.values())
        for msg_type, count in msg_stats.msg_type_statistics.items():
            percentage = (count / total_msgs) * 100
            f_type_stats.write(f"Message Type: {msg_type}, Count: {count}, Percentage: {percentage:.2f}%\n")

    with open("modified_msg_arrival_rate.txt", "w") as f_arrival_rate:
        for msg_type, timestamps in msg_stats.msg_arrival_rate.items():
            if len(timestamps) > 1:
                intervals = [t2 - t1 for t1, t2 in zip(timestamps[:-1], timestamps[1:])]
                intervals_ms = [interval * 1000 for interval in intervals]  # Convert to milliseconds
                f_arrival_rate.write(f"Message Type: {msg_type}, Intervals (ms): {intervals_ms}\n")

    with open("modified_msg_length.txt", "w") as f_msg_length:
        for msg_type, lengths in msg_stats.msg_lengh.items():
            avg_length = sum(lengths) / len(lengths) if lengths else 0
            f_msg_length.write(f"Message Type: {msg_type}, Lengths: {lengths}, Average Length: {avg_length:.2f}\n")

if __name__ == "__main__":
    main()
