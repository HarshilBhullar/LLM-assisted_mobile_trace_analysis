
#!/usr/bin/python
# Filename: modem_debug_analyzer_v2.py

from mobile_insight.analyzer.analyzer import Analyzer

class ModemDebugAnalyzerV2(Analyzer):
    def __init__(self):
        super(ModemDebugAnalyzerV2, self).__init__()
        self.set_source(None)

    def set_source(self, source):
        """
        Set the trace source. Enable the log types for modem debug messages.
        """
        source.enable_log("Modem_debug_message_v2")
        super(ModemDebugAnalyzerV2, self).set_source(source)

    def __msg_callback(self, msg):
        if msg.type_id == "Modem_debug_message_v2":
            self.__process_modem_debug_message(msg)

    def __process_modem_debug_message(self, msg):
        """
        Process modem debug messages and extract relevant information.
        """
        msg_data = msg.data.decode('utf-8', errors='ignore')
        msg_length = len(msg_data)
        self.log_info(f"Modem Debug Message: {msg_data}, Length: {msg_length}")

    def set_source(self, source):
        """
        Set the trace source. Enable necessary log types for analysis.
        """
        source.enable_log("Modem_debug_message_v2")
        super(ModemDebugAnalyzerV2, self).set_source(source)
