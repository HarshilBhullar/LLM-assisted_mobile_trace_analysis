
#!/usr/bin/python
# Filename: lte-measurement-modified
import os
import sys

# Import MobileInsight modules
from mobile_insight.analyzer import *
from mobile_insight.monitor import OnlineMonitor

"""
This example shows how to LTE EMM/ESM layer information with LteNasAnalyzer
with additional filtering on message types.
"""

def filter_messages(message):
    """Filter messages based on specific criteria."""
    # Example: Filter out messages that do not contain "EMM" in their type
    if "EMM" in message.type_id:
        return True
    return False

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

    # Save the analysis result. All analyzers share the same output file.
    dumper.set_log("nas-analyzer-modified.txt")
    nas_analyzer.set_log("nas-analyzer-modified.txt")

    # Start the monitoring with message filtering
    def on_new_message_callback(msg):
        if filter_messages(msg):
            print(f"Processing message: {msg.type_id}")
            # Add additional processing if needed
        else:
            print(f"Ignored message: {msg.type_id}")

    src.set_message_callback(on_new_message_callback)

    # Start the monitoring
    src.run()

# ### Key Modifications:
# 1. **Filtering Functionality:** A `filter_messages()` function was added to filter messages based on specific criteria (e.g., message type containing "EMM"). This function can be extended to include more complex filtering logic as needed.

# 2. **Callback for Message Processing:** A callback function `on_new_message_callback()` was added to process messages conditionally based on the filter criteria.

# 3. **Output Log File:** The log file name was changed to `"nas-analyzer-modified.txt"` to distinguish it from the original analyzer.

# This modified analyzer remains functional and consistent with the existing codebase structure and style while providing an example of how to implement additional processing logic.