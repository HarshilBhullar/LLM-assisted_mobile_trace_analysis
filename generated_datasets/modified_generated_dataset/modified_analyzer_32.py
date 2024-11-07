
#!/usr/bin/python
# Filename: lte-measurement-advanced
import os
import sys

# Import MobileInsight modules
from mobile_insight.analyzer import *
from mobile_insight.monitor import OnlineMonitor

"""
This modified example shows how to obtain advanced LTE EMM/ESM layer information with LteNasAnalyzer
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
    dumper.set_decoding(MsgLogger.JSON)  # decode the message as JSON instead of XML

    nas_analyzer = LteNasAnalyzer()
    nas_analyzer.set_source(src)

    # Apply a different calculation or transformation to the data
    def custom_processing(data):
        # Example transformation: filter and summarize specific metrics
        summary = {"total_messages": len(data), "unique_ids": len(set(item["id"] for item in data))}
        return summary

    nas_analyzer.set_callback(custom_processing)

    # save the analysis result. All analyzers share the same output file.
    dumper.set_log("nas-analyzer-advanced-example.txt")
    nas_analyzer.set_log("nas-analyzer-advanced-example.txt")

    # Start the monitoring
    src.run()
