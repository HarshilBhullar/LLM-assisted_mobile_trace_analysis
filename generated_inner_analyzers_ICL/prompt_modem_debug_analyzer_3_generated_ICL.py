
#!/usr/bin/python
# Filename: modified_modem_debug_analyzer.py
"""
A modified analyzer for processing modem debug messages.
"""

from mobile_insight.analyzer.analyzer import *

__all__ = ["ModifiedModemDebugAnalyzer"]

class ModifiedModemDebugAnalyzer(Analyzer):
    """
    A protocol analyzer for modem debug messages with modifications.
    """

    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)

    def set_source(self, source):
        """
        Set the trace source. Enable the Modem debug messages.

        :param source: the trace source.
        :type source: trace collector
        """
        Analyzer.set_source(self, source)
        source.enable_log("Modem_debug_message")

    def __msg_callback(self, msg):
        """
        Callback function to process Modem debug messages.

        :param msg: the event (message) from the trace collector.
        """
        if msg.type_id == "Modem_debug_message":
            log_item = msg.data.decode()
            if 'Msg' in log_item:
                message = log_item['Msg']
                message_length = len(message)
                self.log_info(f"Original Message: {message}")
                self.log_info(f"Message Length: {message_length}")
