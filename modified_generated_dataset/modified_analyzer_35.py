
#!/usr/bin/python
# Filename: lte-modified-measurement-example
import os
import sys

# Import MobileInsight modules
from mobile_insight.analyzer import *
from mobile_insight.monitor import OnlineMonitor

"""
This example shows how to LTE EMM/ESM layer information with LteNasAnalyzer
with modified analysis capabilities.
"""

if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("Error: please specify physical port name and baudrate.")
        print((__file__, "SERIAL_PORT_NAME BAUNRATE"))
        sys.exit(1)

    # Initialize a DM monitor
    src = OnlineMonitor()
    src.set_serial_port(sys.argv[1])  # the serial port to collect the traces
    src.set_baudrate(int(sys.argv[2]))  # the baudrate of the port

    dumper = MsgLogger()
    dumper.set_source(src)
    dumper.set_decoding(MsgLogger.JSON)  # decode the message as JSON for a change

    nas_analyzer = LteNasAnalyzer()
    nas_analyzer.set_source(src)

    # Introducing a custom metric calculation
    def custom_metric_analysis(data):
        # Placeholder for a new custom metric calculation
        # Example: Calculate average signal strength from data
        if 'signal_strength' in data:
            return sum(data['signal_strength']) / len(data['signal_strength'])
        return None

    # Attach custom analysis to the existing analyzer
    nas_analyzer.custom_analysis = custom_metric_analysis

    # save the analysis result. All analyzers share the same output file.
    dumper.set_log("nas-modified-analyzer-example.txt")
    nas_analyzer.set_log("nas-modified-analyzer-example.txt")

    # Start the monitoring
    src.run()
