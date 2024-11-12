
#!/usr/bin/python
# Filename: modem_debug_analyzer_modified.py
"""
A modified debugger for cellular interface with additional metrics

Author: Yuanjie Li (Modified)
"""

from mobile_insight.analyzer.analyzer import *

__all__ = ["ModemDebugAnalyzerModified"]

class ModemDebugAnalyzerModified(Analyzer):

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
                # Log the original message
                self.log_info(log_item["Msg"])

                # Additional metric: count the number of words in the message
                word_count = len(log_item["Msg"].split())
                self.log_info(f"Word count in message: {word_count}")

                # Additional metric: check if 'Error' keyword is in the message
                if 'Error' in log_item["Msg"]:
                    self.log_info("Error keyword detected in message.")
