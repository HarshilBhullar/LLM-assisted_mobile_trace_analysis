
#!/usr/bin/python
# Filename: modified_msg_statistics.py
"""
A modified analyzer to study the cellular message statistics, arrival interval time, and average message length

Author: Yuanjie Li (Modified)
"""


from mobile_insight.analyzer.analyzer import *

__all__ = ["ModifiedMsgStatistics"]


class ModifiedMsgStatistics(Analyzer):

    def __init__(self):
        Analyzer.__init__(self)

        self.add_source_callback(self.__msg_callback)

        self.msg_type_statistics = {}  # type_id->msg_count

        self.msg_arrival_rate = {}  # type_id->list of arrival interval

        self.msg_lengh = {}  # type_id->list of message length

        self.avg_msg_length = {}  # type_id->average message length

    def reset(self):
        self.msg_type_statistics = {}  # type_id->msg_count

        self.msg_arrival_rate = {}  # type_id->list of arrival interval

        self.msg_lengh = {}  # type_id->list of message length

        self.avg_msg_length = {}  # type_id->average message length

    def set_source(self, source):
        """
        Set the trace source. Enable the cellular signaling messages

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)
        source.enable_log_all()

    def __msg_callback(self, msg):

        log_item = msg.data.decode()

        if msg.type_id not in self.msg_type_statistics:
            self.msg_type_statistics[msg.type_id] = 1
        else:
            self.msg_type_statistics[msg.type_id] += 1

        if msg.type_id not in self.msg_arrival_rate:
            self.msg_arrival_rate[msg.type_id] = [log_item["timestamp"]]
        else:
            self.msg_arrival_rate[msg.type_id].append(log_item["timestamp"])

        if msg.type_id not in self.msg_lengh:
            if "log_msg_len" in log_item:
                self.msg_lengh[msg.type_id] = [log_item["log_msg_len"]]
            elif "Msg Length" in log_item:
                self.msg_lengh[msg.type_id] = [log_item["Msg Length"]]
            elif "Message Length" in log_item:
                self.msg_lengh[msg.type_id] = [log_item["Message Length"]]
        else:
            if "log_msg_len" in log_item:
                self.msg_lengh[msg.type_id].append(log_item["log_msg_len"])
            elif "Msg Length" in log_item:
                self.msg_lengh[msg.type_id].append(log_item["Msg Length"])
            elif "Message Length" in log_item:
                self.msg_lengh[msg.type_id].append(log_item["Message Length"])

        # Calculate average message length
        if msg.type_id in self.msg_lengh:
            total_length = sum(self.msg_lengh[msg.type_id])
            count = len(self.msg_lengh[msg.type_id])
            self.avg_msg_length[msg.type_id] = total_length / count if count > 0 else 0
