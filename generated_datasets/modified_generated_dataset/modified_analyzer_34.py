
#!/usr/bin/python
# Filename: lte-measurement-custom
import os
import sys

# Import MobileInsight modules
from mobile_insight.analyzer import *
from mobile_insight.monitor import OnlineMonitor

"""
This example shows how to perform a custom LTE measurement analysis with LteNasAnalyzer
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

    # Custom processing: filter out specific message types
    class CustomLteNasAnalyzer(LteNasAnalyzer):
        def __init__(self):
            super().__init__()

        def on_receive_msg(self, msg):
            if "NAS" in msg.type_name:  # process only NAS messages
                super().on_receive_msg(msg)

    nas_analyzer = CustomLteNasAnalyzer()
    nas_analyzer.set_source(src)

    # save the analysis result. All analyzers share the same output file.
    dumper.set_log("custom-nas-analyzer-example.txt")
    nas_analyzer.set_log("custom-nas-analyzer-example.txt")

    # Start the monitoring
    src.run()
