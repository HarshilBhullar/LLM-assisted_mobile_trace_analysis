
#!/usr/bin/python
# Filename: outer_mm_analyzer.py

"""
Author: Jiayao Li
"""

from mobile_insight.analyzer.analyzer import Analyzer
from mobile_insight.monitor.offline_replayer import OfflineReplayer
from mobile_insight.analyzer.msg_logger import MsgLogger
from mm_analyzer import MmAnalyzer

def print_additional_metrics(mm_analyzer):
    """
    Calculate and print the total duration of UMTS and LTE normal service spans.
    """
    umts_normal_service_duration = sum(
        (span.end - span.start).total_seconds()
        for span in mm_analyzer.get_umts_normal_service_log()
        if span.end is not None
    )
    lte_normal_service_duration = sum(
        (span.end - span.start).total_seconds()
        for span in mm_analyzer.get_lte_normal_service_log()
        if span.end is not None
    )

    print("UMTS Normal Service Duration: {:.2f} seconds".format(umts_normal_service_duration))
    print("LTE Normal Service Duration: {:.2f} seconds".format(lte_normal_service_duration))


def main():
    """
    Main function to execute the outer analyzer.
    """
    # Initialize OfflineReplayer as the data source
    src = OfflineReplayer()
    src.set_input_path("<path_to_logs_directory>")

    # Create an instance of MsgLogger to log messages in XML format
    msg_logger = MsgLogger()
    msg_logger.set_source(src)
    msg_logger.save_decoded_msg_as("modified_test.txt")

    # Create an instance of MmAnalyzer and set its source
    mm_analyzer = MmAnalyzer()
    mm_analyzer.set_source(src)

    # Run the OfflineReplayer
    src.run()

    # Print additional metrics after monitoring
    print_additional_metrics(mm_analyzer)


if __name__ == "__main__":
    main()
