
#!/usr/bin/python
# Filename: outer_analyzer.py

import sys
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger
from lte_rrc_analyzer import LteRrcAnalyzer

def calculate_additional_metrics(msg):
    """
    Custom function to calculate additional metrics from the LTE_RRC_OTA_Packet messages.
    """
    if msg.type_id == "LTE_RRC_OTA_Packet":
        for field in msg.data.iter('field'):
            if field.get('name') == 'lte-rrc.rsrpResult':
                rsrp = int(field.get('show'))
            if field.get('name') == 'lte-rrc.rsrqResult':
                rsrq = int(field.get('show'))
        
        if 'rsrp' in locals() and 'rsrq' in locals():
            sinr = rsrp - rsrq  # Simplified SINR calculation (for demonstration)
            print(f"Calculated SINR: {sinr}")

def main():
    # Step 1: Monitoring Setup
    replay = OfflineReplayer()
    replay.set_input_path("/path/to/log/directory")  # Set the path to the log directory

    # Enable specific logs
    replay.enable_log("LTE_PHY_Serv_Cell_Measurement")
    replay.enable_log("5G_NR_RRC_OTA_Packet")
    replay.enable_log("LTE_RRC_OTA_Packet")
    replay.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    # Step 2: Message Logging
    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.save_decoded_msg_as("test_modified.txt")
    logger.set_source(replay)  # Bind logger to the OfflineReplayer

    # Step 3: Analyzer Configuration
    lte_rrc_analyzer = LteRrcAnalyzer()
    lte_rrc_analyzer.set_source(replay)

    # Bind custom function to analyzer
    lte_rrc_analyzer.add_source_callback(calculate_additional_metrics)

    # Step 4: Execution
    replay.run()

if __name__ == "__main__":
    main()
