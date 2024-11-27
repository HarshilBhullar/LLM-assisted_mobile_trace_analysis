
#!/usr/bin/python

import sys

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, UlMacLatencyAnalyzer

if __name__ == "__main__":
    try:
        # Initialize a monitor
        src = OfflineReplayer()
        src.set_input_path('./logs/')

        # Enable necessary logs
        src.enable_log("LTE_MAC_UL_Buffer_Status_Internal")
        src.enable_log("5G_NR_RRC_OTA_Packet")
        src.enable_log("LTE_RRC_OTA_Packet")

        # Set up a message logger
        logger = MsgLogger()
        logger.set_decode_format(MsgLogger.XML)
        logger.set_dump_type(MsgLogger.FILE_ONLY)
        logger.save_decoded_msg_as("./ul_mac_latency_log.xml")
        logger.set_source(src)

        # Initialize the custom analyzer
        ulMacLatencyAnalyzer = UlMacLatencyAnalyzer()
        ulMacLatencyAnalyzer.set_source(src)

        # Start the monitoring process
        src.run()

        # Calculate average uplink latency
        pkt_count = len(ulMacLatencyAnalyzer.lat_stat)
        total_latency = sum([stat[4] for stat in ulMacLatencyAnalyzer.lat_stat])
        avg_latency = float(total_latency) / pkt_count if pkt_count > 0 else 0.0

        print("Average uplink packet latency is:", avg_latency)

    except Exception as e:
        print("An error occurred during analysis:", str(e))
