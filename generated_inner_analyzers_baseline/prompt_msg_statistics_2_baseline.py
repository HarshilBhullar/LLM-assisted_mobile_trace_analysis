
from mobile_insight.analyzer.analyzer import Analyzer
from datetime import datetime

class MsgStatisticsModified(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        
        # Initialize data structures
        self.msg_type_statistics = {}
        self.msg_arrival_rate = {}
        self.msg_length = {}
        self.msg_avg_length = {}
        
        # Set a callback for new messages
        self.add_source_callback(self.__msg_callback)

    def set_source(self, source):
        """
        Set the trace source and enable all logs
        """
        self.source = source
        self.source.enable_log_all()

    def __msg_callback(self, msg):
        """
        Callback function to handle each message
        """
        msg_type = msg.type_id
        timestamp = msg.timestamp
        msg_len = self.__get_msg_length(msg)

        # Update Message Type Statistics
        if msg_type not in self.msg_type_statistics:
            self.msg_type_statistics[msg_type] = 0
        self.msg_type_statistics[msg_type] += 1

        # Update Message Arrival Rate
        if msg_type not in self.msg_arrival_rate:
            self.msg_arrival_rate[msg_type] = []
        self.msg_arrival_rate[msg_type].append(timestamp)
        
        # Update Message Length
        if msg_type not in self.msg_length:
            self.msg_length[msg_type] = []
        self.msg_length[msg_type].append(msg_len)

        # Update Average Message Length
        if msg_type not in self.msg_avg_length:
            self.msg_avg_length[msg_type] = 0.0
        total_length = sum(self.msg_length[msg_type])
        self.msg_avg_length[msg_type] = total_length / len(self.msg_length[msg_type])

    def __get_msg_length(self, msg):
        """
        Helper function to extract message length
        """
        if 'log_msg_len' in msg.data.decode():
            return msg.data.decode()['log_msg_len']
        elif 'Msg Length' in msg.data.decode():
            return msg.data.decode()['Msg Length']
        elif 'Message Length' in msg.data.decode():
            return msg.data.decode()['Message Length']
        else:
            return 0
