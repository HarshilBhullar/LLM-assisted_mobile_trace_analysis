
#!/usr/bin/python
# Filename: track-cell-info-analysis.py

"""
Script to analyze LTE RRC messages and cellular data using TrackCellInfoAnalyzer
"""

# Import Required Libraries
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, TrackCellInfoAnalyzer

if __name__ == "__main__":

    try:
        # Initialize a Monitor
        src = OfflineReplayer()
        src.set_input_path("./logs/")

        src.enable_log("LTE_PHY_Serv_Cell_Measurement")
        src.enable_log("5G_NR_RRC_OTA_Packet")
        src.enable_log("LTE_RRC_OTA_Packet")
        src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

        # Set Up Logging
        logger = MsgLogger()
        logger.set_decode_format(MsgLogger.XML)
        logger.set_dump_type(MsgLogger.FILE_ONLY)
        logger.save_decoded_msg_as("./modified_test.txt")
        logger.set_source(src)

        # Integrate TrackCellInfoAnalyzer
        track_cell_info_analyzer = TrackCellInfoAnalyzer()
        track_cell_info_analyzer.set_source(src)

        # Execute the Analysis
        src.run()

        # Retrieve and Print Current Cell Information
        print("Current Cell ID:", track_cell_info_analyzer.get_cur_cell_id())
        print("Current Downlink Frequency:", track_cell_info_analyzer.get_cur_downlink_frequency())
        print("Current Uplink Frequency:", track_cell_info_analyzer.get_cur_uplink_frequency())
        print("Current Downlink Bandwidth:", track_cell_info_analyzer.get_cur_downlink_bandwidth())
        print("Current Uplink Bandwidth:", track_cell_info_analyzer.get_cur_uplink_bandwidth())
        print("Current Operator:", track_cell_info_analyzer.get_cur_op())
        print("Current Band Indicator:", track_cell_info_analyzer.get_cur_band_indicator())
        
    except Exception as e:
        print(f"An error occurred during execution: {e}")
