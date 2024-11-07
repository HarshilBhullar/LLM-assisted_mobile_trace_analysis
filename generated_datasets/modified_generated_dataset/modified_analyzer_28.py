
#!/usr/bin/python
# Filename: lte-measurement-modified
import os
import sys

# Import MobileInsight modules
from mobile_insight.analyzer import LteMeasurementAnalyzer
from mobile_insight.monitor import OnlineMonitor


"""
This modified example shows how to get LTE radio measurements with LteMeasurementAnalyzer,
with additional data processing to calculate average signal strength.
"""

class ModifiedLteMeasurementAnalyzer(LteMeasurementAnalyzer):
    def __init__(self):
        super(ModifiedLteMeasurementAnalyzer, self).__init__()
        self.signal_strengths = []

    def on_measurement(self, msg):
        # Extract signal strength from the measurement message
        signal_strength = msg.get("Signal Strength", 0)
        self.signal_strengths.append(signal_strength)

        # Perform additional analysis: calculate average signal strength
        if len(self.signal_strengths) > 0:
            avg_signal_strength = sum(self.signal_strengths) / len(self.signal_strengths)
            print("Average Signal Strength: {:.2f}".format(avg_signal_strength))

if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("Error: please specify physical port name and baudrate.")
        print((__file__, "SERIAL_PORT_NAME BAUNRATE"))
        sys.exit(1)

    # Initialize a 3G/4G monitor
    src = OnlineMonitor()
    src.set_serial_port(sys.argv[1])  # the serial port to collect the traces
    src.set_baudrate(int(sys.argv[2]))  # the baudrate of the port

    meas_analyzer = ModifiedLteMeasurementAnalyzer()
    meas_analyzer.set_source(src)

    # save the analysis result. All analyzers share the same output file.
    meas_analyzer.set_log("lte-measurement-modified.txt")

    # Start the monitoring
    src.run()
