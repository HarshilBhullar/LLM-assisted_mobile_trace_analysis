#!/usr/bin/python

# Filename: offline_analysis_example.py

import os

import sys

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer

from mobile_insight.analyzer import Analyzer

class myAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)
        self.auth_req_count = 0
        self.security_count = 0
        self.attach_accept_count = 0
        self.attach_req_count = 0
        self.attach_rej_count = 0

    def set_source(self, source):
        """
        Set the trace source. Enable the cellular signaling messages

        :param source: the source monitor
        """
        Analyzer.set_source(self, source)
        source.enable_log_all()  # enable all logs

    def reset_counter(self):
        self.auth_req_count = 0
        self.security_count = 0
        self.attach_accept_count = 0
        self.attach_req_count = 0
        self.attach_rej_count = 0

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_NAS_ESM_PLAIN" or msg.type_id == "LTE_NAS_EMM_PLAIN":  # This is a NAS msg
            log_xml = msg.data.decode_xml()
            if log_xml is None:
                return
            if log_xml.has_element("logcat") and "NasMessageType" in log_xml.get("logcat"):
                msg_type_str = log_xml.get_value("logcat", "NasMessageType")
                if "Authentication request" in msg_type_str:
                    self.auth_req_count += 1
                if "Security mode command" in msg_type_str:
                    self.security_count += 1
                if "Attach accept" in msg_type_str:
                    self.attach_accept_count += 1
                if "Attach request" in msg_type_str:
                    self.attach_req_count += 1
                if "Attach reject" in msg_type_str:
                    self.attach_rej_count += 1

def my_analysis(input_path):
    src = OfflineReplayer()
    src.set_input_path(input_path)

    analyzer = myAnalyzer()
    analyzer.set_source(src)
    try:
        src.run()
    except Exception as e:
        print("Error: analyzer exception %s" % e)
        return None
    return analyzer

if __name__ == "__main__":

    analyzer = my_analysis("./logs/")

    if analyzer is None:
        sys.exit(1)

    row = [src.get_output_path(), analyzer.auth_req_count, analyzer.security_count, analyzer.attach_accept_count, analyzer.attach_req_count, analyzer.attach_rej_count]
    print(row)
    with open("attach_stats.csv", "a") as f:
        f.write(",".join(str(a) for a in row) + "\n")
