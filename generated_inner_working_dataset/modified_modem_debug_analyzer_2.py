
#!/usr/bin/python
# Filename: modem_debug_analyzer_v2.py
"""
A modified debugger for cellular interface

Author: Yuanjie Li
"""


from mobile_insight.analyzer.analyzer import *

__all__ = ["ModemDebugAnalyzerV2"]


class ModemDebugAnalyzerV2(Analyzer):

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
        source.enable_log("Modem_debug_message_v2")

    def __msg_callback(self, msg):

        if msg.type_id == "Modem_debug_message_v2":

            log_item = msg.data.decode()

            # Modified calculation: Log message length
            if 'Msg' in log_item:
                message_content = log_item["Msg"]
                message_length = len(message_content)
                self.log_info(f"Msg: {message_content} (Length: {message_length})")
