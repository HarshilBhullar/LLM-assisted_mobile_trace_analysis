
#!/usr/bin/python
# Filename: lte-measurement-modified
import os
import sys

# Import MobileInsight modules
from mobile_insight.analyzer import LteMeasurementAnalyzer
from mobile_insight.monitor import OnlineMonitor


"""
This modified example shows how to get LTE radio measurements with some additional data processing
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

    # Modify the analyzer to filter out measurements with low signal quality
    def custom_process(measurement):
        # Example: filter out measurements with RSRP (Reference Signal Received Power) less than -100 dBm
        if measurement.get('rsrp', -101) >= -100:
            print("RSRP is acceptable:", measurement['rsrp'])
        else:
            print("Filtered out due to low RSRP:", measurement['rsrp'])

    meas_analyzer.set_callback(custom_process)

    # Save the analysis result. All analyzers share the same output file.
    meas_analyzer.set_log("lte-measurement-modified.txt")

    # Start the monitoring
    src.run()
