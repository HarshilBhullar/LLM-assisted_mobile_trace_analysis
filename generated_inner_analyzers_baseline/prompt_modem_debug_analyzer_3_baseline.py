
from mobileinsight.analyzer.analyzer import Analyzer

class ModifiedModemDebugAnalyzer(Analyzer):
    def __init__(self):
        super().__init__()
        self.add_source_callback(self.__msg_callback)

    def set_source(self, source):
        """
        Set the trace source. Enable the specific log.
        """
        source.enable_log("Modem_debug_message")
        super().set_source(source)

    def __msg_callback(self, msg):
        """
        Callback function to process the modem debug messages.
        """
        if msg.type_id == "Modem_debug_message":
            decoded_msg = msg.data.decode()  # Decoding the message data
            if 'Msg' in decoded_msg:
                message = decoded_msg['Msg']
                message_length = len(message)
                self.log_info(f"Original message: {message}")
                self.log_info(f"Message length: {message_length}")
