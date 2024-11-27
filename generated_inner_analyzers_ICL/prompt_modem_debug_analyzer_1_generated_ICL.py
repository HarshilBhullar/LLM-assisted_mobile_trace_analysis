
#!/usr/bin/python
# Filename: modem_debug_analyzer_modified.py
"""
ModemDebugAnalyzerModified
A modified analyzer to process modem debug messages and extract specific metrics.
"""

__all__ = ["ModemDebugAnalyzerModified"]

from mobile_insight.analyzer.analyzer import Analyzer

class ModemDebugAnalyzerModified(Analyzer):
    """
    A protocol analyzer for Modem Debug messages with specific metrics extraction.
    """

    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)

    def set_source(self, source):
        """
        Set the trace source. Enable the Modem Debug messages.

        :param source: the trace source.
        :type source: trace collector
        """
        Analyzer.set_source(self, source)
        # Enable Modem Debug log
        source.enable_log("Modem_debug_message")

    def __msg_callback(self, msg):
        """
        Process incoming modem debug messages to extract metrics.

        :param msg: the event (message) from the trace collector.
        """
        log_item = msg.data.decode()
        log_message = log_item.get('Message', '')

        # Log the original modem debug message
        self.log_info("Original Message: " + log_message)

        # Compute and log the word count of the message
        word_count = len(log_message.split())
        self.log_info("Word Count: " + str(word_count))

        # Check for the presence of the keyword 'Error' within the message and log its detection
        if 'Error' in log_message:
            self.log_info("Keyword 'Error' Detected in Message")
