
#!/usr/bin/python
# Filename: modified_modem_debug_analyzer.py
"""
A modified debugger for cellular interface

Author: Yuanjie Li
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

        # Phy-layer logs
        source.enable_log("Modem_debug_message")

    def __msg_callback(self, msg):

        if msg.type_id == "Modem_debug_message":

            log_item = msg.data.decode()

            if 'Msg' in log_item:
                message = log_item["Msg"]
                # Perform a simple transformation: calculate the length of the message
                message_length = len(message)
                self.log_info(f"Msg: {message}, Length: {message_length}")
