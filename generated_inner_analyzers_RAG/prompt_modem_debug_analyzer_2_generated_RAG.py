
#!/usr/bin/python
# Filename: modem_debug_analyzer_v2.py

"""
ModemDebugAnalyzerV2
A custom analyzer for processing modem debug messages with length calculation.

Author: Your Name
"""

from mobile_insight.analyzer.analyzer import Analyzer

__all__ = ["ModemDebugAnalyzerV2"]

class ModemDebugAnalyzerV2(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)

    def set_source(self, source):
        """
        Set the trace source. Enable the modem debug messages.

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)
        source.enable_log("Modem_debug_message_v2")

    def __msg_callback(self, msg):
        if msg.type_id == "Modem_debug_message_v2":
            log_item = msg.data.decode()
            message_content = log_item.get('Message Content', '')
            message_length = len(message_content)

            print(f"Modem Debug Message Content: {message_content}")
            print(f"Message Length: {message_length}")
