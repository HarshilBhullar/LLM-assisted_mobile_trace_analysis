
#!/usr/bin/python
# Filename: lte-measurement-modified-example
import os
import sys

# Import MobileInsight modules
from mobile_insight.analyzer import *
from mobile_insight.monitor import OnlineMonitor

"""
This modified example shows how to LTE EMM/ESM layer information with LteNasAnalyzer
and adds additional logging for QoS metrics.
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
    dumper.set_decoding(MsgLogger.XML)  # decode the message as xml

    nas_analyzer = LteNasAnalyzer()
    nas_analyzer.set_source(src)

    # save the analysis result. All analyzers share the same output file.
    dumper.set_log("nas-analyzer-modified-example.txt")
    nas_analyzer.set_log("nas-analyzer-modified-example.txt")

    # Start the monitoring
    src.run()

    # Additional processing for modified analysis
    def process_additional_metrics(nas_analyzer):
        qos = nas_analyzer.get_qos()
        if qos:
            print("Enhanced QoS Information:")
            print(f"  Peak Throughput: {qos.peak_tput} kbps")
            print(f"  Mean Throughput: {qos.mean_tput} kbps")
            print(f"  Max Bitrate Uplink: {qos.max_bitrate_ulink} kbps")
            print(f"  Max Bitrate Downlink: {qos.max_bitrate_dlink} kbps")
            print(f"  Guaranteed Bitrate Uplink: {qos.guaranteed_bitrate_ulink} kbps")
            print(f"  Guaranteed Bitrate Downlink: {qos.guaranteed_bitrate_dlink} kbps")

    # Call the additional processing
    process_additional_metrics(nas_analyzer)
