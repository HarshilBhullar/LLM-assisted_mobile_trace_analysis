
#!/usr/bin/python
# Filename: lte-modified-measurement-example
import os
import sys

# Import MobileInsight modules
from mobile_insight.analyzer import *
from mobile_insight.monitor import OnlineMonitor

"""
This example shows how to perform modified LTE EMM/ESM layer information analysis with LteNasAnalyzer
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

    # Save the analysis result with a different filename and format
    dumper.set_log("modified-nas-analyzer-example.json")
    nas_analyzer.set_log("modified-nas-analyzer-example.json")

    # Implement a simple metric adjustment: log the number of messages processed
    message_count = 0

    def on_message(msg):
        nonlocal message_count
        message_count += 1
        print(f"Processed message count: {message_count}")

    src.set_callback(on_message)

    # Start the monitoring
    src.run()
