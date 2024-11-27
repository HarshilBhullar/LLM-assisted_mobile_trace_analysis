
#!/usr/bin/python
# Filename: ul_mac_latency_analysis.py

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, UlMacLatencyAnalyzer

if __name__ == "__main__":
    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")

    # Enable specific logs
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    # Initialize a logger
    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./modified_test.txt")
    logger.set_source(src)

    # Instantiate the UlMacLatencyAnalyzer
    ul_mac_latency_analyzer = UlMacLatencyAnalyzer()
    ul_mac_latency_analyzer.set_source(src)

    # Custom callback for additional analysis on buffer status
    def custom_callback(msg):
        if msg.type_id == "LTE_MAC_UL_Buffer_Status_Internal":
            log_item = msg.data.decode()
            if 'Subpackets' in log_item:
                total_buffer_length = 0
                sample_count = 0
                for subpkt in log_item['Subpackets']:
                    if 'Samples' in subpkt:
                        for sample in subpkt['Samples']:
                            for lcid in sample['LCIDs']:
                                if 'Total Bytes' in lcid:
                                    total_buffer_length += int(lcid['Total Bytes'])
                                    sample_count += 1
                average_buffer_length = total_buffer_length / sample_count if sample_count > 0 else 0
                print(f"Average Buffer Length: {average_buffer_length} bytes")

    # Add custom callback to the analyzer
    ul_mac_latency_analyzer.add_source_callback(custom_callback)

    # Start the monitoring
    src.run()
