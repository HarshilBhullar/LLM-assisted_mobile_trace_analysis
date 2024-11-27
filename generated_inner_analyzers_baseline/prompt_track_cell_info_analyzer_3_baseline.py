
from mobile_insight.analyzer.analyzer import Analyzer

class LteRrcStatus:
    def __init__(self):
        self.dl_frequency = None
        self.ul_frequency = None
        self.dl_bandwidth = None
        self.ul_bandwidth = None
        self.cell_id = None
        self.tac = None
        self.operator = None
        self.initialized = False

class TrackCellInfoAnalyzerModified(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.set_source(None)
        self.cell_status = LteRrcStatus()

    def set_source(self, source):
        if source:
            source.enable_log("LTE_RRC_Serv_Cell_Info")
            source.enable_log("LTE_RRC_MIB_Packet")
        Analyzer.set_source(self, source)

    def __rrc_filter(self, msg):
        if "LTE_RRC_Serv_Cell_Info" in msg.type_id:
            self.__callback_serv_cell(msg)
        elif "LTE_RRC_MIB_Packet" in msg.type_id:
            self.__callback_mib_cell(msg)

    def __callback_serv_cell(self, msg):
        if not self.cell_status.initialized:
            self.cell_status.initialized = True
            self.cell_status.dl_frequency = msg.data.get("dl_frequency", None)
            self.cell_status.ul_frequency = msg.data.get("ul_frequency", None)
            self.cell_status.dl_bandwidth = msg.data.get("dl_bandwidth", None)
            self.cell_status.cell_id = msg.data.get("cell_id", None)
            self.cell_status.tac = msg.data.get("tac", None)
            mnc = msg.data.get("mnc", None)
            self.cell_status.operator = self.__determine_operator(mnc)
            self.log_info("Initialized cell status: {}".format(self.cell_status))
        else:
            changed = False
            if self.cell_status.dl_frequency != msg.data.get("dl_frequency", None):
                self.cell_status.dl_frequency = msg.data.get("dl_frequency", None)
                changed = True
            if self.cell_status.ul_frequency != msg.data.get("ul_frequency", None):
                self.cell_status.ul_frequency = msg.data.get("ul_frequency", None)
                changed = True
            if self.cell_status.cell_id != msg.data.get("cell_id", None):
                self.cell_status.cell_id = msg.data.get("cell_id", None)
                changed = True
            if self.cell_status.tac != msg.data.get("tac", None):
                self.cell_status.tac = msg.data.get("tac", None)
                changed = True
            if changed:
                self.log_info("Updated cell status: {}".format(self.cell_status))

    def __callback_mib_cell(self, msg):
        self.cell_status.dl_bandwidth = msg.data.get("dl_bandwidth", None)
        self.log_info("MIB cell info updated: DL bandwidth set to {}".format(self.cell_status.dl_bandwidth))

    def __determine_operator(self, mnc):
        operator_map = {
            "01": "Operator_A",
            "02": "Operator_B",
            # Add more mappings as needed
        }
        return operator_map.get(mnc, "Unknown")

    def get_cell_id(self):
        return self.cell_status.cell_id

    def get_tac(self):
        return self.cell_status.tac

    def get_dl_frequency(self):
        return self.cell_status.dl_frequency

    def get_ul_frequency(self):
        return self.cell_status.ul_frequency

    def get_dl_bandwidth(self):
        return self.cell_status.dl_bandwidth

    def get_operator(self):
        return self.cell_status.operator
