
#!/usr/bin/python
# Filename: modified_modem_debug_analyzer.py
"""
A modified debugger for cellular interface

Author: Your Name
"""

from mobile_insight.analyzer.analyzer import *

__all__ = ["ModifiedModemDebugAnalyzer"]

class ModifiedModemDebugAnalyzer(Analyzer):

    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)

    def set_source(self, source):
        """
        Set the trace source. Enable the cellular signaling messages

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)

        # Enable Modem debug messages
        source.enable_log("Modem_debug_message")

    def __msg_callback(self, msg):
        if msg.type_id == "Modem_debug_message":
            log_item = msg.data.decode()

            if 'Msg' in log_item:
                message_content = log_item["Msg"]
                message_length = len(message_content)
                self.log_info(f"Msg: {message_content} (Length: {message_length})")
