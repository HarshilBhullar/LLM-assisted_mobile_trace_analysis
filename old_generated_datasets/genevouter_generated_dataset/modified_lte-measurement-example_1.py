
#!/usr/bin/python
# Filename: lte-measurement-modified-example
import os
import sys

# Import MobileInsight modules
from mobile_insight.analyzer import LteMeasurementAnalyzer
from mobile_insight.monitor import OnlineMonitor


"""
This example shows how to get LTE radio measurements with LteMeasurementAnalyzer and calculate average RSRP and RSRQ
"""

if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("Error: please specify physical port name and baudrate.")
        print((__file__, "SERIAL_PORT_NAME BAUNRATE"))
        sys.exit(1)

    # Initialize a 3G/4G monitor
    src = OnlineMonitor()
    src.set_serial_port(sys.argv[1])  # the serial port to collect the traces
    src.set_baudrate(int(sys.argv[2]))  # the baudrate of the port

    meas_analyzer = LteMeasurementAnalyzer()
    meas_analyzer.set_source(src)

    # Save the analysis result. All analyzers share the same output file.
    meas_analyzer.set_log("lte-measurement-modified-example.txt")

    # Start the monitoring
    src.run()

    # Calculate and print average RSRP and RSRQ
    rsrp_list = meas_analyzer.get_rsrp_list()
    rsrq_list = meas_analyzer.get_rsrq_list()

    if rsrp_list:
        avg_rsrp = sum(rsrp_list) / len(rsrp_list)
        print(f"Average RSRP: {avg_rsrp} dBm")

    if rsrq_list:
        avg_rsrq = sum(rsrq_list) / len(rsrq_list)
        print(f"Average RSRQ: {avg_rsrq} dB")
