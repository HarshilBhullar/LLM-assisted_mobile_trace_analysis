
#!/usr/bin/python
# Filename: outer_analyzer.py

"""
Function: Execute the LteDlRetxAnalyzer to monitor downlink MAC retransmission delay and RLC retransmission delay
Author: Qianru Li
"""

from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.analyzer import MsgLogger
from lte_dl_retx_analyzer import LteDlRetxAnalyzer

def calculate_retx_statistics(analyzer):
    mac_retx_count = 0
    rlc_retx_count = 0

    for entity in analyzer.bearer_entity.values():
        mac_retx_count += len(entity.mac_retx)
        rlc_retx_count += len(entity.rlc_retx)

    print(f"MAC Retransmissions: {mac_retx_count}")
    print(f"RLC Retransmissions: {rlc_retx_count}")

def main():
    # Initialize OfflineReplayer
    src = OfflineReplayer()
    src.set_input_path("trace_logs.mi2log")  # Set the path to your trace logs

    # Enable specific signaling messages
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    # Create an instance of MsgLogger
    logger = MsgLogger()
    logger.set_source(src)
    logger.set_decode_format(MsgLogger.JSON)
    logger.save_decoded_msg_as("decoded_messages.json")  # Specify the file to save messages

    # Create an instance of LteDlRetxAnalyzer
    analyzer = LteDlRetxAnalyzer()
    analyzer.set_source(src)

    # Run the OfflineReplayer to process the logs
    src.run()

    # Calculate and print retransmission statistics
    calculate_retx_statistics(analyzer)

if __name__ == "__main__":
    main()
