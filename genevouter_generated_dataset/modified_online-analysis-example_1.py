
#!/usr/bin/python
# Filename: modified-online-analysis-example.py
import os
import sys

# Import MobileInsight modules
from mobile_insight.analyzer import *
from mobile_insight.monitor import OnlineMonitor

if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("Error: please specify physical port name and baudrate.")
        print((__file__, "SERIAL_PORT_NAME BAUNRATE"))
        sys.exit(1)

    # Initialize a 3G/4G/5G monitor
    src = OnlineMonitor()
    src.set_serial_port(sys.argv[1])  # the serial port to collect the traces
    src.set_baudrate(int(sys.argv[2]))  # the baudrate of the port

    # Enable 3G/4G/5G RRC (radio resource control) monitoring
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("WCDMA_RRC_OTA_Packet")

    # 5G NR RRC analyzer
    nr_rrc_analyzer = NrRrcAnalyzer()
    nr_rrc_analyzer.set_source(src)  # bind with the monitor

    # 4G RRC analyzer
    lte_rrc_analyzer = LteRrcAnalyzer()
    lte_rrc_analyzer.set_source(src)  # bind with the monitor

    # 3G RRC analyzer
    wcdma_rrc_analyzer = WcdmaRrcAnalyzer()
    wcdma_rrc_analyzer.set_source(src)  # bind with the monitor

    # Start the monitoring
    src.run()

    # Additional processing: Log the list of cells the device has associated with
    print("Cell List: ", nr_rrc_analyzer.get_cell_list())

    # Additional processing: Log the current cell's configuration if available
    current_config = nr_rrc_analyzer.get_cur_cell_config()
    if current_config:
        print("Current Cell Configuration: ", current_config.dump())
    else:
        print("No current cell configuration available.")
