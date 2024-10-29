
#!/usr/bin/python
# Filename: lte-modified-measurement-example
import os
import sys

# Import MobileInsight modules
from mobile_insight.analyzer import LteMeasurementAnalyzer
from mobile_insight.monitor import OnlineMonitor


"""
This modified example shows how to get LTE radio measurements with LteMeasurementAnalyzer
and applies additional processing to the measurements.
"""

def process_measurement(data):
    """
    Example function to process measurement data.
    This function could apply transformations, filtering, or compute additional metrics.
    """
    # For demonstration, let's assume we apply a simple transformation
    # such as scaling the measurement values by a factor of 2.
    processed_data = {k: v * 2 for k, v in data.items()}
    return processed_data

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

    # Override the callback function to apply additional processing
    def on_measurement_callback(data):
        # Process the measurement data
        processed_data = process_measurement(data)
        # Log the processed data
        with open("lte-modified-measurement-example.txt", "a") as f:
            f.write(str(processed_data) + "\n")

    meas_analyzer.on_measurement = on_measurement_callback

    # Start the monitoring
    src.run()
