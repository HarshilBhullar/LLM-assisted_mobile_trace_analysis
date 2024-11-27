
#!/usr/bin/python

import sys
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.msg_statistics import MsgStatistics

def analyze_msg_statistics(input_path):
    src = OfflineReplayer()
    src.set_input_path(input_path)

    statistics = MsgStatistics()
    statistics.set_source(src)

    src.run()

    # Save message type statistics
    with open('msg_type_statistics.txt', 'w') as f_statistics:
        for item in statistics.msg_type_statistics:
            f_statistics.write(f"{item} {statistics.msg_type_statistics[item]}\n")

    # Save message arrival rate statistics
    with open('msg_arrival_rate.txt', 'w') as f_rate:
        for item in statistics.msg_arrival_rate:
            f_rate.write(f"{item} ")
            for k in range(1, len(statistics.msg_arrival_rate[item])):
                interval = (statistics.msg_arrival_rate[item][k] - statistics.msg_arrival_rate[item][k - 1]).total_seconds() * 1000
                f_rate.write(f"{interval} ")
            f_rate.write("\n")

    # Save message length statistics
    with open('msg_length_summary.txt', 'w') as f_msg_len:
        for item in statistics.msg_lengh:
            total_length = sum(statistics.msg_lengh[item])
            average_length = total_length / len(statistics.msg_lengh[item]) if statistics.msg_lengh[item] else 0
            f_msg_len.write(f"{item} Total Length: {total_length} Average Length: {average_length}\n")

if __name__ == "__main__":
    input_path = sys.argv[1]
    analyze_msg_statistics(input_path)
