
#!/usr/bin/python
# Filename: lte-measurement-modified
import os
import sys

# Import MobileInsight modules
from mobile_insight.analyzer import LteMeasurementAnalyzer
from mobile_insight.monitor import OnlineMonitor


"""
This modified example shows how to get LTE radio measurements with LteMeasurementAnalyzer
with additional processing to calculate the average signal strength.
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

    # Additional processing to calculate average signal strength
    def process_measurements(measurements):
        total_signal_strength = 0
        count = 0
        for measurement in measurements:
            if 'signal_strength' in measurement:
                total_signal_strength += measurement['signal_strength']
                count += 1
        if count > 0:
            avg_signal_strength = total_signal_strength / count
            print("Average Signal Strength:", avg_signal_strength)
        else:
            print("No valid signal strength data available.")

    meas_analyzer.set_callback(process_measurements)

    # Save the analysis result. All analyzers share the same output file.
    meas_analyzer.set_log("lte-measurement-modified.txt")

    # Start the monitoring
    src.run()
