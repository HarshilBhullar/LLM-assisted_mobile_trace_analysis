
#!/usr/bin/python
# Filename: outer_wcdma_rrc_analyzer.py

from mobile_insight.analyzer import MsgLogger
from mobile_insight.analyzer.analyzer import ProtocolAnalyzer
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer.protocol_analyzer import WcdmaRrcAnalyzer


class ExtendedWcdmaRrcAnalyzer(WcdmaRrcAnalyzer):
    def __init__(self):
        super().__init__()
        self.rrc_state_counts = {
            'CELL_FACH': 0,
            'CELL_DCH': 0,
            'URA_PCH': 0,
            'CELL_PCH': 0,
            'IDLE': 0
        }

    def __rrc_filter(self, msg):
        super().__rrc_filter(msg)
        if msg.type_id == "WCDMA_RRC_States":
            rrc_state = str(msg.data['RRC State'])
            if rrc_state in self.rrc_state_counts:
                self.rrc_state_counts[rrc_state] += 1

    def print_state_counts(self):
        for state, count in self.rrc_state_counts.items():
            print(f"{state}: {count}")


def main():
    # Initialize OfflineReplayer
    src = OfflineReplayer()
    src.set_input_path("/path/to/log/directory")  # Set the path to the log directory here

    # Enable specific logs
    src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    # Initialize and set up MsgLogger
    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as("/path/to/save/decoded_messages.xml")  # Set the path to save the XML file

    # Attach logger to the source (OfflineReplayer)
    logger.set_source(src)

    # Initialize ExtendedWcdmaRrcAnalyzer and attach to the source
    analyzer = ExtendedWcdmaRrcAnalyzer()
    analyzer.set_source(src)

    # Run the replayer
    src.run()

    # Print the RRC state counts
    analyzer.print_state_counts()


if __name__ == "__main__":
    main()
