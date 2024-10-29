#!/usr/bin/python
# Filename: lte-enhanced-measurement-example
import os
import sys

# Import MobileInsight modules
from mobile_insight.analyzer import LteMeasurementAnalyzer
from mobile_insight.monitor import OnlineMonitor

"""
This example shows how to get enhanced LTE radio measurements with LteMeasurementAnalyzer.
An adjustment factor is applied to the measurements in this version.
"""

ADJUSTMENT_FACTOR = 1.1  # Hypothetical adjustment factor for demonstration purposes

class EnhancedLteMeasurementAnalyzer(LteMeasurementAnalyzer):
    def __init__(self):
        super().__init__()

    def on_measurement(self, measurement):
        # Apply an adjustment factor to each measurement value
        adjusted_measurement = {key: value * ADJUSTMENT_FACTOR for key, value in measurement.items()}
        self.log_adjusted_measurement(adjusted_measurement)

    def log_adjusted_measurement(self, measurement):
        with open(self.get_log(), "a") as log_file:
            log_file.write(f"Adjusted Measurement: {measurement}\n")

if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("Error: please specify physical port name and baudrate.")
        print((__file__, "SERIAL_PORT_NAME BAUNRATE"))
        sys.exit(1)

    # Initialize a 3G/4G monitor
    src = OnlineMonitor()
    src.set_serial_port(sys.argv[1])  # the serial port to collect the traces
    src.set_baudrate(int(sys.argv[2]))  # the baudrate of the port

    meas_analyzer = EnhancedLteMeasurementAnalyzer()
    meas_analyzer.set_source(src)

    # Save the analysis result. All analyzers share the same output file.
    meas_analyzer.set_log("lte-enhanced-measurement-example.txt")

    # Start the monitoring
    src.run()
# ### Key Modifications:
# 1. **Enhanced Analyzer Class**: Introduced a new class `EnhancedLteMeasurementAnalyzer` that inherits from `LteMeasurementAnalyzer`. This allows us to override or extend the functionality specific to this analyzer.
# 2. **Adjustment Factor**: Added a constant `ADJUSTMENT_FACTOR` that is applied to each measurement to simulate a change in the analysis process.
# 3. **Adjusting Measurements**: The `on_measurement` method applies the adjustment factor to the incoming measurements, demonstrating how you might alter data processing.
# 4. **Logging Adjusted Measurements**: A new method `log_adjusted_measurement` writes the adjusted measurements to the log file.

# This modified analyzer maintains the style and structure of the existing codebase while introducing a simple change to the data processing logic.