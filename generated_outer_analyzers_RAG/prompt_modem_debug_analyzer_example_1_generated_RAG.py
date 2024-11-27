
#!/usr/bin/python
# Filename: modified-offline-analysis-example.py

# Import necessary modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, ModemDebugAnalyzer

def custom_callback(msg_counter):
    def callback(msg):
        if msg.type_id == "Modem_debug_message":
            msg_counter[0] += 1
    return callback

def main():
    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")

    # Enable additional logs
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")
    
    # Setup logger
    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("test_modified.txt")
    logger.set_source(src)

    # Initialize ModemDebugAnalyzer
    modem_debug_analyzer = ModemDebugAnalyzer()
    modem_debug_analyzer.set_source(src)

    # Custom callback to count modem debug messages
    msg_counter = [0]
    modem_debug_analyzer.add_source_callback(custom_callback(msg_counter))

    # Start the monitoring
    src.run()

    # Print the total number of messages processed
    print(f"Total 'Modem_debug_message' messages processed: {msg_counter[0]}")

if __name__ == "__main__":
    main()
