
#!/usr/bin/python
# Filename: msg_statistics_modified.py
"""
msg_statistics_modified.py
A modified analyzer to evaluate basic statistics of cellular messages in an offline log.
"""

__all__ = ["MsgStatisticsModified"]

from mobile_insight.analyzer import Analyzer
from datetime import datetime

class MsgStatisticsModified(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.msg_type_statistics = {}  # Message type -> count
        self.msg_arrival_rate = {}  # Message type -> list of arrival times
        self.msg_length = {}  # Message type -> list of lengths
        self.avg_msg_length = {}  # Message type -> average length

        self.add_source_callback(self.__msg_callback)

    def set_source(self, source):
        """
        Set the trace source. Enable all cellular signaling messages.

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)
        source.enable_log_all()

    def __msg_callback(self, msg):
        msg_type = msg.type_id
        timestamp = msg.timestamp
        log_item = msg.data.decode()

        # Update message type statistics
        if msg_type not in self.msg_type_statistics:
            self.msg_type_statistics[msg_type] = 0
        self.msg_type_statistics[msg_type] += 1

        # Update message arrival rate
        if msg_type not in self.msg_arrival_rate:
            self.msg_arrival_rate[msg_type] = []
        self.msg_arrival_rate[msg_type].append(timestamp)

        # Update message length
        msg_len = 0
        if 'log_msg_len' in log_item:
            msg_len = log_item['log_msg_len']
        elif 'Msg Length' in log_item:
            msg_len = log_item['Msg Length']
        elif 'Message Length' in log_item:
            msg_len = log_item['Message Length']

        if msg_type not in self.msg_length:
            self.msg_length[msg_type] = []
        self.msg_length[msg_type].append(msg_len)

        # Calculate average message length
        self.avg_msg_length[msg_type] = sum(self.msg_length[msg_type]) / len(self.msg_length[msg_type])
