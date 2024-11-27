
#!/usr/bin/python
# Filename: lte_rrc_offline_analysis.py

"""
Offline analysis by replaying LTE RRC logs
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, LteRrcAnalyzer

if __name__ == "__main__":

    # Initialize a monitor
    src = OfflineReplayer()
    src.set_input_path("./logs/")
    # src.enable_log_all()

    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("./test_modified.txt")
    logger.set_source(src)

    # Analyzers
    lte_rrc_analyzer = LteRrcAnalyzer()
    lte_rrc_analyzer.set_source(src)  # bind with the monitor

    # Additional calculation: calculate SINR from RRC messages
    def calculate_additional_metrics(msg):
        if msg.type_id == "LTE_RRC_OTA_Packet":
            sinr = None
            rsrp = None
            rsrq = None
            for field in msg.data.iter('field'):
                if field.get('name') == 'lte-rrc.rsrpResult':
                    rsrp = int(field.get('show')) - 141  # Convert to dBm
                if field.get('name') == 'lte-rrc.rsrqResult':
                    rsrq = (int(field.get('show')) / 2.0) - 19.5  # Convert to dB

            if rsrp is not None and rsrq is not None:
                sinr = rsrp - rsrq
                print(f"SINR: {sinr} dB")

    lte_rrc_analyzer.add_source_callback(calculate_additional_metrics)

    # Start the monitoring
    src.run()
