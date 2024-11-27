
#!/usr/bin/python
# Filename: msg_statistics_modified.py

"""
msg_statistics_modified.py
An analyzer to evaluate basic statistics of cellular messages in an offline log with additional metrics

Author: [Your Name]
"""

from mobile_insight.analyzer.analyzer import *

__all__ = ["MsgStatisticsModified"]

class MsgStatisticsModified(Analyzer):
    """
    A modified analyzer to evaluate basic statistics of cellular messages
    """
    
    def __init__(self):
        Analyzer.__init__(self)
        
        self.msg_type_statistics = {}
        self.msg_arrival_rate = {}
        self.msg_length = {}
        self.avg_msg_length = {}
        
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

        # Update Message Type Statistics
        if msg_type not in self.msg_type_statistics:
            self.msg_type_statistics[msg_type] = 0
        self.msg_type_statistics[msg_type] += 1

        # Update Message Arrival Rate
        if msg_type not in self.msg_arrival_rate:
            self.msg_arrival_rate[msg_type] = []
        self.msg_arrival_rate[msg_type].append(timestamp)

        # Update Message Length
        msg_len = self.__get_msg_length(log_item)
        if msg_type not in self.msg_length:
            self.msg_length[msg_type] = []
        self.msg_length[msg_type].append(msg_len)

        # Calculate Average Message Length
        if msg_type not in self.avg_msg_length:
            self.avg_msg_length[msg_type] = 0
        total_length = sum(self.msg_length[msg_type])
        count = len(self.msg_length[msg_type])
        self.avg_msg_length[msg_type] = total_length / count if count > 0 else 0

    def __get_msg_length(self, log_item):
        """
        Helper method to extract message length from log item.
        """
        if 'log_msg_len' in log_item:
            return int(log_item['log_msg_len'])
        elif 'Msg Length' in log_item:
            return int(log_item['Msg Length'])
        elif 'Message Length' in log_item:
            return int(log_item['Message Length'])
        else:
            return 0  # Default to 0 if no length field is found
