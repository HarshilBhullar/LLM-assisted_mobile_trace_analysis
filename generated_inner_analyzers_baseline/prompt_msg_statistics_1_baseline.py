
import datetime
from mobile_insight.analyzer import Analyzer

class MsgStatisticsModified(Analyzer):
    def __init__(self):
        super(MsgStatisticsModified, self).__init__()
        self.msg_type_statistics = {}
        self.msg_arrival_rate = {}
        self.msg_length = {}
        self.msg_average_length = {}
        self.last_msg_time = {}

    def set_source(self, source):
        super(MsgStatisticsModified, self).set_source(source)
        source.enable_log("LTE_NAS_EMM_OTA_Incoming_Packet")
        source.enable_log("LTE_NAS_EMM_OTA_Outgoing_Packet")
        source.enable_log("LTE_NAS_ESM_OTA_Incoming_Packet")
        source.enable_log("LTE_NAS_ESM_OTA_Outgoing_Packet")

    def __msg_callback(self, msg):
        log_item = msg.data.decode()
        msg_type = log_item.get("Message Type", "Unknown")
        timestamp = datetime.datetime.fromtimestamp(msg.timestamp)
        
        # Update message type count
        if msg_type not in self.msg_type_statistics:
            self.msg_type_statistics[msg_type] = 0
        self.msg_type_statistics[msg_type] += 1

        # Update message arrival intervals
        if msg_type not in self.msg_arrival_rate:
            self.msg_arrival_rate[msg_type] = []
        if msg_type in self.last_msg_time:
            interval = (timestamp - self.last_msg_time[msg_type]).total_seconds() * 1000
            self.msg_arrival_rate[msg_type].append(interval)
        self.last_msg_time[msg_type] = timestamp

        # Update message lengths
        msg_length = log_item.get("log_msg_len", log_item.get("Msg Length", log_item.get("Message Length", 0)))
        if msg_type not in self.msg_length:
            self.msg_length[msg_type] = []
        self.msg_length[msg_type].append(msg_length)

        # Calculate average message length
        total_length = sum(self.msg_length[msg_type])
        self.msg_average_length[msg_type] = total_length / len(self.msg_length[msg_type])

    def reset(self):
        self.msg_type_statistics.clear()
        self.msg_arrival_rate.clear()
        self.msg_length.clear()
        self.msg_average_length.clear()
        self.last_msg_time.clear()
