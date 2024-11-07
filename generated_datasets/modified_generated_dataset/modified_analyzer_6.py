
#!/usr/bin/python
# Filename: custom-monitor-analyzer.py

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

    # Save the monitoring results as an offline log
    src.save_log_as("./custom-monitor-example.mi2log")

    # Enable 3G/4G/5G messages to be monitored. Here we enable RRC 
    # (radio resource control) monitoring and additional messages
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("WCDMA_RRC_OTA_Packet")
    src.enable_log("NR_DL_CCCH_Message")  # New message type
    src.enable_log("LTE_NAS_EMM_State")  # New message type

    # Initialize message counter dictionary
    message_count = {
        "5G_NR_RRC_OTA_Packet": 0,
        "LTE_RRC_OTA_Packet": 0,
        "WCDMA_RRC_OTA_Packet": 0,
        "NR_DL_CCCH_Message": 0,
        "LTE_NAS_EMM_State": 0
    }

    # Message callback function to count messages
    def msg_callback(msg):
        msg_type = msg.type_id
        if msg_type in message_count:
            message_count[msg_type] += 1

    # Set message callback
    src.set_callback(msg_callback)

    # Dump the messages to std I/O. Comment it if it is not needed.
    dumper = MsgLogger()
    dumper.set_source(src)
    dumper.set_decoding(MsgLogger.XML)  # decode the message as xml

    # Start the monitoring
    src.run()

    # Output the message count statistics
    print("Message Count Statistics:")
    for msg_type, count in message_count.items():
        print(f"{msg_type}: {count}")

# ### Explanation of Changes:
# 1. **Additional Message Types**: The modified analyzer enables logging for additional message types: `NR_DL_CCCH_Message` and `LTE_NAS_EMM_State`. These are just examples; you can choose different message types based on your needs.

# 2. **Message Counting**: A simple counter is introduced to keep track of how many messages of each type are received. This helps in understanding the distribution of message types.

# 3. **Callback Function**: A callback function `msg_callback` is added to process messages as they are received, updating the message count accordingly.

# 4. **Output Statistics**: After the monitoring is complete, the script prints out the message count statistics, providing a simple analysis of the collected data.

# This modified analyzer remains consistent with the style and structure of the existing codebase while introducing new functionality.