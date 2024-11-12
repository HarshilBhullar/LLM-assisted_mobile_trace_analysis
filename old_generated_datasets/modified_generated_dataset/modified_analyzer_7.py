#!/usr/bin/python
# Filename: modified-msg-statistics-example.py

import os
import sys

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.msg_statistics import MsgStatistics

"""
This example shows how to get enhanced statistics of an offline log,
including average message length per message type.
"""
if __name__ == "__main__":

    # Initialize a 3G/4G monitor
    src = OfflineReplayer()
    src.set_input_path("./offline_log_example.mi2log")

    statistics = MsgStatistics()
    statistics.set_source(src)

    # Start the monitoring
    src.run()

    # Save basic message type statistics
    with open('./msg_type_statistics.txt', 'w') as f_statistics:
        for item in statistics.msg_type_statistics:
            f_statistics.write(
                item + " " + str(statistics.msg_type_statistics[item]) + "\n")

    # Save message arrival rates
    with open('./msg_arrival_rate.txt', 'w') as f_rate:
        for item in statistics.msg_arrival_rate:
            f_rate.write(item + " ")
            for k in range(1, len(statistics.msg_arrival_rate[item])):
                f_rate.write(str(
                    (statistics.msg_arrival_rate[item][k] - statistics.msg_arrival_rate[item][k - 1]).total_seconds() * 1000) + " ")
            f_rate.write("\n")

    # Save message lengths and calculate average length
    with open('./msg_length.txt', 'w') as f_msg_len, open('./msg_avg_length.txt', 'w') as f_avg_len:
        for item in statistics.msg_lengh:
            msg_lengths = statistics.msg_lengh[item]
            total_length = sum(msg_lengths)
            avg_length = total_length / len(msg_lengths) if msg_lengths else 0

            # Write individual message lengths
            f_msg_len.write(item + " ")
            for length in msg_lengths:
                f_msg_len.write(str(length) + " ")
            f_msg_len.write("\n")

            # Write average message length
            f_avg_len.write(item + " " + str(avg_length) + "\n")

# ### Key Modifications:
# 1. **Average Message Length Calculation:**
#    - A new calculation for the average message length per message type is introduced and saved to `msg_avg_length.txt`.

# 2. **Use of Context Managers:**
#    - The code now uses Python's `with` statement for file operations to ensure that files are properly closed, which enhances readability and reliability.

# 3. **Additional Comments:**
#    - Additional comments have been added to improve code readability and to explain new calculations.

# This modified analyzer remains functional and adheres to the style and structure of the original codebase, while providing additional insights into the data.