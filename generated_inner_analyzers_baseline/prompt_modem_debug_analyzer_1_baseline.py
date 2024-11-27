
from mobile_insight.analyzer.analyzer import Analyzer

class ModemDebugAnalyzerModified(Analyzer):
    def __init__(self):
        super(ModemDebugAnalyzerModified, self).__init__()
        self.add_source_callback(self.__msg_callback)

    def set_source(self, source):
        """
        Set the data source of the analyzer.
        """
        super(ModemDebugAnalyzerModified, self).set_source(source)
        source.enable_log("Modem_debug_message")

    def __msg_callback(self, msg):
        """
        Callback function for processing each modem debug message.
        """
        # Decode the message
        message_str = msg.data.decode("utf-8", errors="ignore")

        # Log the original modem debug message
        self.log_info("Original Modem Debug Message: {}".format(message_str))

        # Compute and log the word count of the message
        word_count = len(message_str.split())
        self.log_info("Word Count: {}".format(word_count))

        # Check for the presence of the keyword 'Error' in the message
        if 'Error' in message_str:
            self.log_info("Keyword 'Error' detected in the message.")
