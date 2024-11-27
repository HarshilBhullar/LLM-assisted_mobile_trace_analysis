
#!/usr/bin/python

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger
from modem_debug_analyzer import ModemDebugAnalyzer

if __name__ == "__main__":

    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")

    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./test_modified.txt")
    logger.set_source(src)

    modem_debug_analyzer = ModemDebugAnalyzer()
    modem_debug_analyzer.set_source(src)

    # Additional processing: Count total number of "Modem_debug_message"
    message_count = 0

    def count_debug_messages(msg):
        nonlocal message_count
        if msg.type_id == "Modem_debug_message":
            message_count += 1

    modem_debug_analyzer.add_source_callback(count_debug_messages)

    # Start the monitoring
    src.run()

    # Output the additional metric
    print(f"Total number of 'Modem_debug_message' messages processed: {message_count}")
