
from mobile_insight.analyzer.analyzer import Analyzer

class TrackCellInfoAnalyzerModified(Analyzer):
    def __init__(self):
        super(TrackCellInfoAnalyzerModified, self).__init__()

        # Internal states to store cell information
        self.dl_frequency = None
        self.ul_frequency = None
        self.bandwidth = None
        self.tac = None
        self.operator = None
        self.cell_id = None
        self.allowed_access = None
        self.num_antennas = None
        self.physical_cell_id = None

    def set_source(self, source):
        super(TrackCellInfoAnalyzerModified, self).set_source(source)
        source.enable_log("LTE_RRC_Serv_Cell_Info")
        source.enable_log("LTE_RRC_MIB_Packet")

    def get_average_frequency(self):
        if self.dl_frequency and self.ul_frequency:
            return (self.dl_frequency + self.ul_frequency) / 2
        return None

    def get_current_cell_status(self):
        return {
            "cell_id": self.cell_id,
            "tac": self.tac,
            "dl_frequency": self.dl_frequency,
            "ul_frequency": self.ul_frequency,
            "bandwidth": self.bandwidth,
            "allowed_access": self.allowed_access,
            "operator": self.operator,
            "average_frequency": self.get_average_frequency(),
            "num_antennas": self.num_antennas,
            "physical_cell_id": self.physical_cell_id
        }

    def decode_msg(self, msg):
        if msg.type_id == "LTE_RRC_Serv_Cell_Info":
            self.__handle_lte_rrc_serv_cell_info(msg)
        elif msg.type_id == "LTE_RRC_MIB_Packet":
            self.__handle_lte_rrc_mib_packet(msg)

    def __handle_lte_rrc_serv_cell_info(self, msg):
        # Extract and update the current cell status
        try:
            log_item = msg.data.decode()
            self.dl_frequency = log_item.get("dl_frequency", None)
            self.ul_frequency = log_item.get("ul_frequency", None)
            self.bandwidth = log_item.get("bandwidth", None)
            self.cell_id = log_item.get("cell_id", None)
            self.tac = log_item.get("tac", None)
            self.operator = log_item.get("operator", None)
            self.allowed_access = log_item.get("allowed_access", None)

            # Compute average frequency
            avg_freq = self.get_average_frequency()

            # Broadcast the updated cell status including average frequency
            self.broadcast_info(self.get_current_cell_status())
        except Exception as e:
            self.log_warning("Failed to parse LTE_RRC_Serv_Cell_Info: %s" % str(e))

    def __handle_lte_rrc_mib_packet(self, msg):
        # Extract MIB-related information
        try:
            log_item = msg.data.decode()
            self.num_antennas = log_item.get("num_antennas", None)
            self.physical_cell_id = log_item.get("physical_cell_id", None)

            # Broadcast MIB information
            self.broadcast_info({
                "num_antennas": self.num_antennas,
                "physical_cell_id": self.physical_cell_id
            })
        except Exception as e:
            self.log_warning("Failed to parse LTE_RRC_MIB_Packet: %s" % str(e))
