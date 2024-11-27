
#!/usr/bin/python
# Filename: msg_statistics_modified.py
"""
MsgStatisticsModified.py
An analyzer to monitor statistics for cellular messages, including message type counts, arrival intervals, and average message lengths.
"""

from .analyzer import *

__all__ = ["MsgStatisticsModified"]


class MsgStatisticsModified(Analyzer):
    """
    Analyze cellular message statistics, including message type counts, arrival intervals, and average message lengths.
    """

    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)
        
        # Initialize dictionaries to store statistics
        self.msg_type_statistics = {}
        self.msg_arrival_rate = {}
        self.msg_length = {}
        self.msg_avg_length = {}

    def set_source(self, source):
        """
        Set the trace source. Enable all cellular signaling messages.

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)

        # Enable all logs
        source.enable_log_all()

    def __msg_callback(self, msg):
        """
        Callback function to process each message and update statistics.
        """
        msg_type = msg.type_id
        timestamp = msg.timestamp
        msg_len = msg.data.get('log_msg_len', msg.data.get('Msg Length', msg.data.get('Message Length', 0)))

        # Update message type count
        if msg_type not in self.msg_type_statistics:
            self.msg_type_statistics[msg_type] = 0
            self.msg_arrival_rate[msg_type] = []
            self.msg_length[msg_type] = []
        self.msg_type_statistics[msg_type] += 1

        # Record the timestamp for arrival interval calculation
        self.msg_arrival_rate[msg_type].append(timestamp)

        # Record the message length
        self.msg_length[msg_type].append(msg_len)

        # Calculate average message length
        total_length = sum(self.msg_length[msg_type])
        self.msg_avg_length[msg_type] = total_length / len(self.msg_length[msg_type])

    def reset(self):
        """
        Reset all statistics, allowing the analyzer to be reused.
        """
        self.msg_type_statistics.clear()
        self.msg_arrival_rate.clear()
        self.msg_length.clear()
        self.msg_avg_length.clear()
