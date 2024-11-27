
#!/usr/bin/python
# Filename: run_lte_measurement_analysis.py

from mobile_insight.analyzer import MsgLogger
from mobile_insight.monitor import OfflineReplayer
from lte_measurement_analyzer import LteMeasurementAnalyzer

def main():
    # Initialize OfflineReplayer as the data source
    src = OfflineReplayer()
    src.set_input_path("/path/to/log/files")  # Set the correct path to the log files

    # Enable necessary logs for analysis
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    # Set up MsgLogger to log messages
    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.save_decoded_msg_as("modified_test.txt")
    logger.set_source(src)

    # Integrate the custom LteMeasurementAnalyzer
    lte_analyzer = LteMeasurementAnalyzer()
    lte_analyzer.set_source(src)

    # Define a function to compute additional metrics
    def log_additional_metrics():
        rsrp_list = lte_analyzer.get_rsrp_list()
        rsrq_list = lte_analyzer.get_rsrq_list()
        
        if rsrp_list:
            avg_rsrp = sum(rsrp_list) / len(rsrp_list)
            print(f"Average RSRP: {avg_rsrp:.2f} dBm")
        
        if rsrq_list:
            avg_rsrq = sum(rsrq_list) / len(rsrq_list)
            print(f"Average RSRQ: {avg_rsrq:.2f} dB")

    # Execute the monitoring and analysis
    src.run()
    log_additional_metrics()

if __name__ == "__main__":
    main()
