
#!/usr/bin/python
# Filename: modified_msg_statistics.py
"""
A modified analyzer to study cellular message statistics, arrival interval time, and average message length.

Author: Yuanjie Li
"""

from mobile_insight.analyzer.analyzer import *

__all__ = ["ModifiedMsgStatistics"]

import datetime

class ModifiedMsgStatistics(Analyzer):

    def __init__(self):
        Analyzer.__init__(self)

        self.add_source_callback(self.__msg_callback)

        self.msg_type_statistics = {}  # type_id -> msg_count
        self.msg_arrival_rate = {}  # type_id -> list of arrival timestamps
        self.msg_length = {}  # type_id -> list of message lengths
        self.avg_msg_length = {}  # type_id -> average message length

    def reset(self):
        self.msg_type_statistics = {}
        self.msg_arrival_rate = {}
        self.msg_length = {}
        self.avg_msg_length = {}

    def set_source(self, source):
        """
        Set the trace source. Enable all cellular signaling messages.

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)
        source.enable_log_all()

    def __msg_callback(self, msg):
        msg_type = msg.type_id
        msg_timestamp = msg.timestamp

        if msg_type not in self.msg_type_statistics:
            self.msg_type_statistics[msg_type] = 0
            self.msg_arrival_rate[msg_type] = []
            self.msg_length[msg_type] = []
            self.avg_msg_length[msg_type] = 0

        # Update message count
        self.msg_type_statistics[msg_type] += 1

        # Record message arrival timestamp
        self.msg_arrival_rate[msg_type].append(msg_timestamp)

        # Capture message length
        log_item = msg.data.decode()
        if 'Msg' in log_item:
            message_content = log_item["Msg"]
            message_length = len(message_content)
            self.msg_length[msg_type].append(message_length)

            # Compute average message length
            total_length = sum(self.msg_length[msg_type])
            self.avg_msg_length[msg_type] = total_length / len(self.msg_length[msg_type])

            self.log_info(f"Processed message type: {msg_type}, Length: {message_length}, Average Length: {self.avg_msg_length[msg_type]:.2f}")
