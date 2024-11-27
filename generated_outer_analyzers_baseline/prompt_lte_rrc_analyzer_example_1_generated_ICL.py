
#!/usr/bin/python
# Filename: modified_lte_rrc_analyzer.py
"""
A script for offline analysis using ModifiedLteRrcAnalyzer.
Author: Yuanjie Li, Zhehui Zhang
"""

import os
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import LteRrcAnalyzer
from mobile_insight.analyzer import MsgLogger

class ModifiedLteRrcAnalyzer(LteRrcAnalyzer):
    """
    A modified analyzer that adds functionality to calculate new metrics like Signal Quality Index (SQI).
    """

    def __init__(self):
        super(ModifiedLteRrcAnalyzer, self).__init__()

    def __rrc_filter(self, msg):
        super(ModifiedLteRrcAnalyzer, self).__rrc_filter(msg)
        # Calculate additional metrics like SQI here
        # Example: Calculate SQI based on RSRP and RSRQ
        if msg.type_id == "MEAS_PCELL":
            rsrp = msg.data.get('rsrp', None)
            rsrq = msg.data.get('rsrq', None)
            if rsrp is not None and rsrq is not None:
                sqi = self.calculate_sqi(rsrp, rsrq)
                self.send_to_coordinator(Event(msg.timestamp, 'sqi', sqi))

    def calculate_sqi(self, rsrp, rsrq):
        # Placeholder for actual SQI calculation logic
        # This function should return an SQI value based on the given RSRP and RSRQ
        return (rsrp + rsrq) / 2

if __name__ == "__main__":
    # Directory containing log files
    log_dir = "path/to/log/directory"

    # Create an OfflineReplayer to read log files
    src = OfflineReplayer()
    src.set_input_path(log_dir)

    # Set up a MsgLogger to save decoded messages
    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.JSON)
    logger.save_decoded_msg_as("decoded_messages.json")

    # Create and configure an instance of ModifiedLteRrcAnalyzer
    analyzer = ModifiedLteRrcAnalyzer()

    # Bind logger and analyzer to the OfflineReplayer
    analyzer.set_source(src)
    logger.set_source(src)

    # Execute the monitor to process the logs
    src.run()
