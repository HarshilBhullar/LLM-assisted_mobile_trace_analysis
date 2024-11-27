
#!/usr/bin/python

from mobile_insight.monitor import OfflineReplayer, MsgLogger
from mobile_insight.analyzer import LteMeasurementAnalyzer

def log_additional_metrics(analyzer):
    rsrp_list = analyzer.get_rsrp_list()
    rsrq_list = analyzer.get_rsrq_list()

    if rsrp_list:
        avg_rsrp = sum(rsrp_list) / len(rsrp_list)
        print("Average RSRP: {:.2f} dBm".format(avg_rsrp))
    else:
        print("No RSRP data available.")

    if rsrq_list:
        avg_rsrq = sum(rsrq_list) / len(rsrq_list)
        print("Average RSRQ: {:.2f} dB".format(avg_rsrq))
    else:
        print("No RSRQ data available.")

if __name__ == "__main__":
    # Initialize OfflineReplayer
    src = OfflineReplayer()
    src.set_input_path('./logs/offline_log_examples/')

    # Enable specific logs
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    # Set up MsgLogger
    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.save_decoded_msg_as("./modified_test.txt")
    logger.set_source(src)

    # Set up LteMeasurementAnalyzer
    analyzer = LteMeasurementAnalyzer()
    analyzer.set_source(src)

    # Run the OfflineReplayer
    src.run()

    # Log additional metrics
    log_additional_metrics(analyzer)
