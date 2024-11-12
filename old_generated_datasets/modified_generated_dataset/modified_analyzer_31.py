
#!/usr/bin/python
# Filename: lte-modified-measurement-example
import os
import sys

# Import MobileInsight modules
from mobile_insight.analyzer import *
from mobile_insight.monitor import OnlineMonitor

"""
This modified example shows how to LTE EMM/ESM layer information with LteNasAnalyzer
with adjusted metrics for analysis.
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

    # Adjusted metric calculation: log additional metrics
    nas_analyzer.set_additional_metrics(['RSRP', 'RSRQ'])

    # save the analysis result. All analyzers share the same output file.
    dumper.set_log("modified-nas-analyzer-example.txt")
    nas_analyzer.set_log("modified-nas-analyzer-example.txt")

    # Start the monitoring
    src.run()
