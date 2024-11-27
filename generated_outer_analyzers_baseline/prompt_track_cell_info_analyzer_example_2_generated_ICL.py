
#!/usr/bin/python
# Filename: outer_track_cell_info_analyzer.py

"""
An outer analyzer for tracking LTE cell information using TrackCellInfoAnalyzer.

Author: Yuanjie Li, Zhehui Zhang
"""

from mobile_insight.analyzer import OfflineReplayer
from mobile_insight.analyzer.analyzer import MsgLogger
from track_cell_info_analyzer import TrackCellInfoAnalyzer

def main():
    # Initialize the OfflineReplayer as the data source
    src = OfflineReplayer()
    src.set_input_path("path/to/trace/logs")  # Specify the input path for the trace logs

    # Enable LTE RRC logs and other relevant logs
    src.enable_log("LTE_RRC_Serv_Cell_Info")
    src.enable_log("LTE_RRC_MIB_Packet")

    # Set up a MsgLogger to log messages in XML format
    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_path("path/to/output/logs.xml")
    logger.set_source(src)

    # Instantiate TrackCellInfoAnalyzer and set it as a source for the OfflineReplayer
    analyzer = TrackCellInfoAnalyzer()
    analyzer.set_source(src)

    # Define a function to calculate additional metrics after processing logs
    def calculate_metrics():
        total_bandwidth = analyzer.get_cur_downlink_bandwidth() + analyzer.get_cur_uplink_bandwidth()
        print(f"Total Bandwidth: {total_bandwidth} MHz")
        print(f"Current Operator: {analyzer.get_cur_op()}")
        print(f"Current Cell ID: {analyzer.get_cur_cell_id()}")
        print(f"Current TAC: {analyzer.get_cur_cell_tac()}")

    # Run the OfflineReplayer to start processing the logs
    src.run()

    # Execute additional metric calculations after logs have been processed
    calculate_metrics()

if __name__ == "__main__":
    main()
