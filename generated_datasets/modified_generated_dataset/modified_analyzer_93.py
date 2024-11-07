
#!/usr/bin/python
# Filename: modified-lte-measurement-example
import os
import sys

# Import MobileInsight modules
from mobile_insight.analyzer import *
from mobile_insight.monitor import OnlineMonitor

"""
This example shows how to perform modified LTE EMM/ESM layer analysis with LteNasAnalyzer
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
    dumper.set_decoding(MsgLogger.JSON)  # decode the message as JSON

    nas_analyzer = LteNasAnalyzer()
    nas_analyzer.set_source(src)

    # Adjust the log file name to reflect the modified analysis
    dumper.set_log("modified-nas-analyzer-example.txt")
    nas_analyzer.set_log("modified-nas-analyzer-example.txt")

    # Example modification: filter messages based on a specific condition
    def custom_callback(message):
        # Process only messages containing specific keywords
        if "Attach" in message or "Detach" in message:
            print("Filtered Message: ", message)

    nas_analyzer.set_callback(custom_callback)

    # Start the monitoring
    src.run()
