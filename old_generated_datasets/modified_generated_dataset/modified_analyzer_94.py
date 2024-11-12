
#!/usr/bin/python
# Filename: modified-lte-measurement-example
import os
import sys

# Import MobileInsight modules
from mobile_insight.analyzer import *
from mobile_insight.monitor import OnlineMonitor

"""
This example shows how to perform a modified LTE EMM/ESM layer information analysis with a custom analyzer
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

    # Assume we have a CustomNasAnalyzer for demonstration purposes
    class CustomNasAnalyzer(LteNasAnalyzer):
        def __init__(self):
            super().__init__()

        def process_message(self, message):
            # Adding a custom processing step: count message types
            message_type = message.get('message_type', 'unknown')
            print(f"Processing message type: {message_type}")

            # Call the parent class's process_message
            super().process_message(message)

    nas_analyzer = CustomNasAnalyzer()
    nas_analyzer.set_source(src)

    # save the analysis result with a different log file
    dumper.set_log("modified-nas-analyzer-example.txt")
    nas_analyzer.set_log("modified-nas-analyzer-example.txt")

    # Start the monitoring
    src.run()
