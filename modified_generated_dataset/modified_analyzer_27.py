
#!/usr/bin/python
# Filename: lte-enhanced-measurement
import os
import sys

# Import MobileInsight modules
from mobile_insight.analyzer import LteMeasurementAnalyzer
from mobile_insight.monitor import OnlineMonitor


"""
This enhanced example shows how to get LTE radio measurements with LteMeasurementAnalyzer
with additional processing for signal quality metrics.
"""

class EnhancedLteMeasurementAnalyzer(LteMeasurementAnalyzer):
    def __init__(self):
        super().__init__()
        self.signal_quality_threshold = -100  # Example threshold for signal quality

    def callback(self, msg):
        # Call the parent class's callback method
        super().callback(msg)

        # Additional processing for enhanced metrics
        # Example: Filter and count messages with signal quality above a threshold
        signal_quality = self.extract_signal_quality(msg)
        if signal_quality > self.signal_quality_threshold:
            print(f"Good signal quality detected: {signal_quality}")

    def extract_signal_quality(self, msg):
        # Placeholder for actual logic to extract signal quality from msg
        # This could be RSRP, RSRQ, SINR, etc.
        return -95  # Example static value for demonstration

if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("Error: please specify physical port name and baudrate.")
        print((__file__, "SERIAL_PORT_NAME BAUNRATE"))
        sys.exit(1)

    # Initialize a 3G/4G monitor
    src = OnlineMonitor()
    src.set_serial_port(sys.argv[1])  # the serial port to collect the traces
    src.set_baudrate(int(sys.argv[2]))  # the baudrate of the port

    # Use the enhanced analyzer
    meas_analyzer = EnhancedLteMeasurementAnalyzer()
    meas_analyzer.set_source(src)

    # Save the analysis result. All analyzers share the same output file.
    meas_analyzer.set_log("lte-enhanced-measurement.txt")

    # Start the monitoring
    src.run()
