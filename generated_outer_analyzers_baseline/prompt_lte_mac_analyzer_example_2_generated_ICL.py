
#!/usr/bin/python
# Filename: outer_lte_mac_analyzer.py

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger
from lte_mac_analyzer import LteMacAnalyzer

def custom_metric_processing():
    """
    Perform additional metric calculations or data processing after the log replay and analysis.
    """
    print("Custom metric processing completed.")

def main():
    # Initialize the offline replayer
    src = OfflineReplayer()
    
    # Set input path for logs directory
    src.set_input_path("path/to/logs_directory")  # Replace with the actual path to the logs directory
    
    # Enable specific logs required for the analysis
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")
    
    # Set up the log recording
    logger = MsgLogger()
    logger.set_source(src)
    logger.set_decoded_log("decoded_logs.xml")  # Specify the file format and path for storing decoded messages
    
    # Integrate the LteMacAnalyzer
    lte_mac_analyzer = LteMacAnalyzer()
    lte_mac_analyzer.set_source(src)
    
    # Start the log replay
    src.run()
    
    # Execute custom metric processing after replay and analysis
    custom_metric_processing()

if __name__ == "__main__":
    main()
