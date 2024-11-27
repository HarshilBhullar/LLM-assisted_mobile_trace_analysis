
#!/usr/bin/python
# Filename: outer_lte_mac_analyzer.py

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger
from lte_mac_analyzer import LteMacAnalyzer

def main():
    # Initialize OfflineReplayer to replay logs from a specified directory
    src = OfflineReplayer()
    src.set_input_path("<path_to_log_directory>")  # Set the correct path to your log directory

    # Enable specific logs for LTE and 5G signaling messages
    src.enable_log("LTE_MAC_UL_Tx_Statistics")
    src.enable_log("LTE_MAC_UL_Buffer_Status_Internal")
    src.enable_log("LTE_PHY_PDSCH_Stat_Indication")

    # Set up a MsgLogger to decode and save messages to a file
    logger = MsgLogger()
    logger.set_source(src)
    logger.set_decode_format(MsgLogger.JSON)
    logger.save_decoded_msg_as("<output_file_path>")  # Set the correct path for output file

    # Instantiate LteMacAnalyzer and set it to use OfflineReplayer as its data source
    analyzer = LteMacAnalyzer()
    analyzer.set_source(src)

    # Variables for calculating average UL grant utilization
    total_grant_received = 0
    total_grant_utilized = 0

    # Callback function for custom processing of UL Tx statistics
    def custom_callback(msg):
        if msg.type_id == "MAC_UL_GRANT":
            data = msg.data
            total_grant_received += int(data['received'])
            total_grant_utilized += int(data['used'])

    # Register the custom callback to LteMacAnalyzer
    analyzer.add_source_callback(custom_callback)

    # Run the offline replay to trigger the analysis
    src.run()

    # Calculate and print the average UL grant utilization
    if total_grant_received > 0:
        avg_utilization = (total_grant_utilized / total_grant_received) * 100
        print(f"Average UL Grant Utilization: {avg_utilization:.2f}%")
    else:
        print("No data available for UL Grant Utilization.")

if __name__ == "__main__":
    main()
