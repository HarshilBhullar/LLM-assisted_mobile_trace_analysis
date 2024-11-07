
#!/usr/bin/python
# Filename: lte-modified-analyzer
import os
import sys

# Import MobileInsight modules
from mobile_insight.analyzer import LteMeasurementAnalyzer
from mobile_insight.monitor import OnlineMonitor

"""
This example shows how to get LTE radio measurements with LteMeasurementAnalyzer
with additional filtering based on signal strength.
"""

class CustomLteMeasurementAnalyzer(LteMeasurementAnalyzer):
    def __init__(self):
        super(CustomLteMeasurementAnalyzer, self).__init__()

    def on_measurement(self, event):
        # Simply log the measurements that have signal strength above a threshold
        signal_strength_threshold = -85  # in dBm
        if 'RSRP' in event.data and event.data['RSRP'] > signal_strength_threshold:
            print(f"Strong signal detected: RSRP = {event.data['RSRP']} dBm")
            super(CustomLteMeasurementAnalyzer, self).on_measurement(event)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("Error: please specify physical port name and baudrate.")
        print((__file__, "SERIAL_PORT_NAME BAUNRATE"))
        sys.exit(1)

    # Initialize a 3G/4G monitor
    src = OnlineMonitor()
    src.set_serial_port(sys.argv[1])  # the serial port to collect the traces
    src.set_baudrate(int(sys.argv[2]))  # the baudrate of the port

    meas_analyzer = CustomLteMeasurementAnalyzer()
    meas_analyzer.set_source(src)

    # save the analysis result. All analyzers share the same output file.
    meas_analyzer.set_log("lte-modified-analyzer.txt")

    # Start the monitoring
    src.run()
