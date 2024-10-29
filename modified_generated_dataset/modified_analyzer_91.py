
#!/usr/bin/python
# Filename: lte-modified-measurement-example
import os
import sys

# Import MobileInsight modules
from mobile_insight.analyzer import LteMeasurementAnalyzer
from mobile_insight.monitor import OnlineMonitor


"""
This modified example shows how to get LTE radio measurements with LteMeasurementAnalyzer
and apply additional data processing.
"""

def custom_metric_processing(data):
    # Example of custom processing: average signal strength
    signal_strengths = [entry['signal_strength'] for entry in data if 'signal_strength' in entry]
    if signal_strengths:
        return sum(signal_strengths) / len(signal_strengths)
    return None

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
    meas_analyzer.set_log("lte-modified-measurement-example.txt")

    # Adding a custom callback for additional processing
    def on_measurement_callback(msg):
        data = msg.data.decode()  # Assuming data is JSON-encoded
        processed_metric = custom_metric_processing(data)
        if processed_metric is not None:
            print(f"Processed Metric (Average Signal Strength): {processed_metric}")

    meas_analyzer.add_callback(on_measurement_callback)

    # Start the monitoring
    src.run()
