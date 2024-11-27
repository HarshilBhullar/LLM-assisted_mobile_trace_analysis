
#!/usr/bin/python
# Filename: lte_measurement_outer_analyzer.py
"""
Outer analyzer for LTE radio measurements

Author: Yuanjie Li
"""

from mobile_insight.analyzer import OfflineReplayer
from mobile_insight.monitor import MsgLogger
from lte_measurement_analyzer import LteMeasurementAnalyzer

def calculate_average(measurements):
    """
    Calculate the average of a list of measurements.

    :param measurements: List of numeric measurements
    :returns: Average value or None if the list is empty
    """
    if not measurements:
        return None
    return sum(measurements) / len(measurements)

def print_average_metrics(analyzer):
    """
    Print average RSRP and RSRQ metrics from the analyzer.

    :param analyzer: Instance of LteMeasurementAnalyzer
    """
    rsrp_list = analyzer.get_rsrp_list()
    rsrq_list = analyzer.get_rsrq_list()

    avg_rsrp = calculate_average(rsrp_list)
    avg_rsrq = calculate_average(rsrq_list)

    if avg_rsrp is not None:
        print(f"Average RSRP: {avg_rsrp:.2f} dBm")
    else:
        print("No RSRP measurements available.")

    if avg_rsrq is not None:
        print(f"Average RSRQ: {avg_rsrq:.2f} dB")
    else:
        print("No RSRQ measurements available.")

def main():
    # Initialize OfflineReplayer
    src = OfflineReplayer()
    src.set_input_path("path/to/your/logs")

    # Configure MsgLogger
    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.save_decoded_msg_as("decoded_messages.xml")

    # Integrate LteMeasurementAnalyzer
    analyzer = LteMeasurementAnalyzer()
    analyzer.set_source(src)

    # Start the monitoring process
    src.run()

    # Print calculated average metrics
    print_average_metrics(analyzer)

if __name__ == "__main__":
    main()
