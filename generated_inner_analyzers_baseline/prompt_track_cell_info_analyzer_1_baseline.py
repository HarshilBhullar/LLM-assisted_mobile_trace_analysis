
from mobile_insight.analyzer.analyzer import Analyzer

class TrackCellInfoAnalyzerModified(Analyzer):
    def __init__(self):
        super(TrackCellInfoAnalyzerModified, self).__init__()
        self._state = {
            "cell_id": None,
            "tac": None,
            "frequency": None,
            "dl_bandwidth": None,
            "ul_bandwidth": None,
            "operator": None,
            "num_antennas": None,
            "additional_metric": None
        }
        self.add_source_callback(self.__rrc_filter)

    def __rrc_filter(self, msg):
        if msg.type_id == "LTE_RRC_Serv_Cell_Info":
            self.__callback_serv_cell(msg.data.decode())
        elif msg.type_id == "LTE_RRC_MIB_Packet":
            self.__callback_mib_cell(msg.data.decode())

    def __callback_serv_cell(self, data):
        if not self._state["cell_id"]:
            # Initialize cell status
            self._state["cell_id"] = data.get("Cell ID")
            self._state["tac"] = data.get("Tracking Area Code")
            self._state["frequency"] = data.get("Frequency Band Indicator")
            self._state["operator"] = data.get("MNC")
        
        self._state["dl_bandwidth"] = data.get("Downlink Bandwidth")
        self._state["ul_bandwidth"] = data.get("Uplink Bandwidth")

        # Calculate additional metric
        self._state["additional_metric"] = self.calculate_additional_metric(
            self._state["dl_bandwidth"], self._state["ul_bandwidth"])
        self.log_info("Additional Metric: {}".format(self._state["additional_metric"]))

    def __callback_mib_cell(self, data):
        self._state["num_antennas"] = data.get("Number of Antennas")
        self._state["dl_bandwidth"] = data.get("Downlink Bandwidth")

    def calculate_additional_metric(self, dl_bandwidth, ul_bandwidth):
        if dl_bandwidth is not None and ul_bandwidth is not None:
            return dl_bandwidth * ul_bandwidth
        return None

    def set_source(self, source):
        self.set_source_callback(source)
        source.enable_log("LTE_RRC_Serv_Cell_Info")
        source.enable_log("LTE_RRC_MIB_Packet")

    def get_cell_id(self):
        return self._state["cell_id"]

    def get_tac(self):
        return self._state["tac"]

    def get_frequency(self):
        return self._state["frequency"]

    def get_dl_bandwidth(self):
        return self._state["dl_bandwidth"]

    def get_ul_bandwidth(self):
        return self._state["ul_bandwidth"]

    def get_operator(self):
        return self._state["operator"]

    def get_num_antennas(self):
        return self._state["num_antennas"]

    def get_additional_metric(self):
        return self._state["additional_metric"]
