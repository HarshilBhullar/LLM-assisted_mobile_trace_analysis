
#!/usr/bin/python
# Filename: run_track_cell_info.py

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, TrackCellInfoAnalyzer

def main():
    try:
        # Initialize the offline replayer
        src = OfflineReplayer()
        src.set_input_path("./logs/")  # Directory containing the log files
        
        # Enable necessary logs
        src.enable_log("LTE_PHY_Serv_Cell_Measurement")
        src.enable_log("5G_NR_RRC_OTA_Packet")
        src.enable_log("LTE_RRC_OTA_Packet")
        src.enable_log("LTE_NB1_ML1_GM_DCI_Info")
        
        # Set up message logger
        logger = MsgLogger()
        logger.set_decode_format(MsgLogger.XML)
        logger.set_dump_path("./modified_test.txt")
        logger.set_source(src)
        
        # Initialize TrackCellInfoAnalyzer
        analyzer = TrackCellInfoAnalyzer()
        analyzer.set_source(src)
        
        # Run the analysis
        src.run()
        
        # Retrieve and print current cell information
        print("Cell ID:", analyzer.get_cur_cell_id())
        print("Downlink Frequency:", analyzer.get_cur_downlink_frequency())
        print("Uplink Frequency:", analyzer.get_cur_uplink_frequency())
        print("Operator:", analyzer.get_cur_op())
        print("Band Indicator:", analyzer.get_cur_band_indicator())
        
    except Exception as e:
        print("An error occurred during execution:", str(e))

if __name__ == "__main__":
    main()
