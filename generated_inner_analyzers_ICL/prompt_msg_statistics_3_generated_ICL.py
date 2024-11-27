
#!/usr/bin/python
# Filename: modified_msg_statistics.py

from mobile_insight.analyzer.analyzer import Analyzer
from collections import defaultdict
import datetime

__all__ = ["ModifiedMsgStatistics"]

class ModifiedMsgStatistics(Analyzer):

    def __init__(self):
        Analyzer.__init__(self)

        self.add_source_callback(self.__msg_callback)
        
        # Initialize counters and lists
        self.msg_type_statistics = defaultdict(int)
        self.msg_arrival_rate = defaultdict(list)
        self.msg_length = defaultdict(list)
        self.avg_msg_length = defaultdict(float)

    def set_source(self, source):
        """
        Set the trace source. Enable all cellular signaling messages.

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)

        # Enable all signaling messages
        source.enable_log_all()

    def __msg_callback(self, msg):
        """
        Process each message to update statistics

        :param msg: the event (message) from the trace collector.
        """
        msg_type = msg.type_id
        timestamp = msg.timestamp
        msg_length = len(msg.data.decode())

        # Update message count for each type
        self.msg_type_statistics[msg_type] += 1
        
        # Record timestamp to calculate arrival intervals
        self.msg_arrival_rate[msg_type].append(timestamp)
        
        # Capture and store message length
        self.msg_length[msg_type].append(msg_length)

        # Compute the average message length
        total_length = sum(self.msg_length[msg_type])
        count = len(self.msg_length[msg_type])
        self.avg_msg_length[msg_type] = total_length / count
