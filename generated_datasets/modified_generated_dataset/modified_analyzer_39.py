
#!/usr/bin/python
# Filename: modified-monitor-example.py
import os
import sys

# Import MobileInsight modules
from mobile_insight.monitor import OnlineMonitor
from mobile_insight.analyzer import MsgLogger

if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("Error: please specify physical port name and baudrate.")
        print((__file__, "SERIAL_PORT_NAME BAUNRATE"))
        sys.exit(1)

    # Initialize a 3G/4G/5G monitor
    src = OnlineMonitor()
    src.set_serial_port(sys.argv[1])  # the serial port to collect the traces
    src.set_baudrate(int(sys.argv[2]))  # the baudrate of the port

    # Save the monitoring results as an offline log with a different filename
    src.save_log_as("./modified-monitor-example.mi2log")

    # Enable 3G/4G/5G messages to be monitored. Here we enable RRC (radio
    # resource control) monitoring with an additional log
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("WCDMA_RRC_OTA_Packet")
    src.enable_log("WCDMA_RRC_Serv_Cell_Info")  # Un-commented to enable

    # Dump the messages to std I/O with JSON decoding instead of XML
    dumper = MsgLogger()
    dumper.set_source(src)
    dumper.set_decoding(MsgLogger.JSON)  # decode the message as JSON

    # Start the monitoring
    src.run()
