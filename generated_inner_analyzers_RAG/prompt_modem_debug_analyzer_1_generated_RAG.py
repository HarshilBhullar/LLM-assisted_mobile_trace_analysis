
#!/usr/bin/python
# Filename: modem_debug_analyzer_modified.py

"""
A modified analyzer to process modem debug messages and extract specific metrics.
"""

from mobile_insight.analyzer.analyzer import *

__all__ = ["ModemDebugAnalyzerModified"]


class ModemDebugAnalyzerModified(Analyzer):
    """
    A modified analyzer to process modem debug messages.
    """

    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)

    def set_source(self, source):
        """
        Set the source of the trace.
        Enable modem debug message logs.

        :param source: the source trace collector
        :param type: trace collector
        """
        Analyzer.set_source(self, source)
        source.enable_log("Modem_debug_message")

    def __msg_callback(self, msg):
        """
        Callback to handle modem debug messages.

        :param msg: the message from the trace collector
        :type msg: trace message
        """
        log_item = msg.data.decode()

        # Log the original modem debug message
        self.log_info("Modem Debug Message: " + log_item)

        # Compute and log the word count of the message
        word_count = len(log_item.split())
        self.log_info("Word Count: " + str(word_count))

        # Check for the presence of the keyword 'Error' and log its detection
        if 'Error' in log_item:
            self.log_info("Keyword 'Error' detected in message.")
