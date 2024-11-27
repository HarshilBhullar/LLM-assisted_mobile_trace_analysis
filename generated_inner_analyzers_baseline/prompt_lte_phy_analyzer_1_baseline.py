
from mobile_insight.analyzer.analyzer import Analyzer

class LtePhyAnalyzerModified(Analyzer):
    def __init__(self):
        super(LtePhyAnalyzerModified, self).__init__()
        self.dl_bandwidth = 0
        self.ul_bandwidth = 0
        self.cqi_values = []
        self.cqi_to_bw_mapping = {
            0: 0, 1: 1.4, 2: 1.4, 3: 2.8, 4: 2.8,
            5: 5.0, 6: 5.0, 7: 10.0, 8: 10.0, 9: 15.0,
            10: 20.0, 11: 20.0, 12: 20.0, 13: 20.0,
            14: 20.0, 15: 20.0
        }

    def set_source(self, source):
        super(LtePhyAnalyzerModified, self).set_source(source)
        source.enable_log("LTE_PHY_PDSCH_Packet")
        source.enable_log("LTE_PHY_PUSCH_CSF")
        source.enable_log("LTE_MAC_UL_Tx_Statistics")
        source.enable_log("LTE_PHY_PUCCH_Tx_Report")
        source.enable_log("LTE_PHY_PUSCH_Tx_Report")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_PHY_PDSCH_Packet":
            self.handle_pdsch_packet(msg)
        elif msg.type_id == "LTE_PHY_PUSCH_CSF":
            self.handle_pusch_csf(msg)
        elif msg.type_id == "LTE_MAC_UL_Tx_Statistics":
            self.handle_ul_tx_statistics(msg)
        elif msg.type_id == "LTE_PHY_PUCCH_Tx_Report":
            self.handle_pucch_tx_report(msg)
        elif msg.type_id == "LTE_PHY_PUSCH_Tx_Report":
            self.handle_pusch_tx_report(msg)

    def handle_pdsch_packet(self, msg):
        cqi = msg.data.get("cqi", [])
        if cqi:
            self.cqi_values.extend(cqi)
            predicted_bw = self.predict_bw(cqi)
            self.log_info("Predicted Downlink Bandwidth: {} MHz".format(predicted_bw))

    def handle_pusch_csf(self, msg):
        cqi = msg.data.get("cqi", [])
        if cqi:
            self.cqi_values.extend(cqi)
            self.log_info("Uplink CQI values: {}".format(cqi))

    def handle_ul_tx_statistics(self, msg):
        ul_grant = msg.data.get("ul_grant", 0)
        self.ul_bandwidth += ul_grant
        self.log_info("Uplink Grant Utilization: {}".format(ul_grant))

    def handle_pucch_tx_report(self, msg):
        sr_events = msg.data.get("scheduling_request", [])
        self.log_info("PUCCH Scheduling Requests: {}".format(sr_events))

    def handle_pusch_tx_report(self, msg):
        power_measurements = msg.data.get("power_meas", [])
        self.log_info("PUSCH Power Measurements: {}".format(power_measurements))

    def predict_bw(self, cqi_list):
        total_bw = 0
        for cqi in cqi_list:
            total_bw += self.cqi_to_bw_mapping.get(cqi, 0)
        average_bw = total_bw / len(cqi_list) if cqi_list else 0
        return average_bw

    def log_info(self, message):
        print(message)

    def set_source(self, source):
        super(LtePhyAnalyzerModified, self).set_source(source)
        source.enable_log("LTE_PHY_PDSCH_Packet")
        source.enable_log("LTE_PHY_PUSCH_CSF")
        source.enable_log("LTE_MAC_UL_Tx_Statistics")
        source.enable_log("LTE_PHY_PUCCH_Tx_Report")
        source.enable_log("LTE_PHY_PUSCH_Tx_Report")
