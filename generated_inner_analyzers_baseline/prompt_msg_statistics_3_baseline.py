
from mobile_insight.analyzer.analyzer import Analyzer
from datetime import datetime

class ModifiedMsgStatistics(Analyzer):
    def __init__(self):
        super(ModifiedMsgStatistics, self).__init__()
        self.msg_type_statistics = {}
        self.msg_arrival_rate = {}
        self.msg_length = {}
        self.last_msg_time = {}

    def set_source(self, source):
        super(ModifiedMsgStatistics, self).set_source(source)
        source.enable_log("LTE_RRC_OTA_Packet")
        source.enable_log("WCDMA_RRC_OTA_Packet")
        source.enable_log("GSM_RR_OTA_Packet")
        source.enable_log("5G_NR_RRC_OTA_Packet")

    def __msg_callback(self, msg):
        msg_type = msg.type_id
        msg_timestamp = msg.timestamp
        msg_length = len(msg.data.decode('utf-8', errors='ignore'))

        # Update message count
        if msg_type not in self.msg_type_statistics:
            self.msg_type_statistics[msg_type] = 0
        self.msg_type_statistics[msg_type] += 1

        # Update message arrival rate
        if msg_type not in self.msg_arrival_rate:
            self.msg_arrival_rate[msg_type] = []
        self.msg_arrival_rate[msg_type].append(msg_timestamp)

        # Update message lengths
        if msg_type not in self.msg_length:
            self.msg_length[msg_type] = []
        self.msg_length[msg_type].append(msg_length)

        # Calculate average message length
        total_length = sum(self.msg_length[msg_type])
        count = len(self.msg_length[msg_type])
        avg_length = total_length / count
        print(f"Average length for {msg_type}: {avg_length}")

    def run(self):
        self.set_callback(self.__msg_callback)
