#!/usr/bin/python

from mobile_insight.analyzer.analyzer import Analyzer
from mobile_insight.monitor import OfflineReplayer
import csv

class myAnalyzer(Analyzer):
    def __init__(self):
        super(myAnalyzer, self).__init__()
        self.auth_requests_count = 0
        self.security_commands_count = 0
        self.attach_accepts_count = 0
        self.attach_requests_count = 0
        self.attach_rejections_count = 0

    def __msg_callback(self, msg):
        # Process each message to identify specific NAS message types
        if msg.type_id == "LTE_NAS_ESM_MSG":
            if msg.attach_request:
                self.attach_requests_count += 1
            elif msg.attach_accept:
                self.attach_accepts_count += 1
            elif msg.attach_reject:
                self.attach_rejections_count += 1
        elif msg.type_id == "LTE_NAS_EMM_MSG":
            if msg.auth_request:
                self.auth_requests_count += 1
            elif msg.security_command:
                self.security_commands_count += 1

    def my_analysis(self):
        src = OfflineReplayer()
        src.set_input_path("./logs/")
        src.add_source_callback(self.__msg_callback)
        src.run()

        return {
            "auth_requests": self.auth_requests_count,
            "security_commands": self.security_commands_count,
            "attach_accepts": self.attach_accepts_count,
            "attach_requests": self.attach_requests_count,
            "attach_rejections": self.attach_rejections_count
        }

if __name__ == "__main__":
    analyzer = myAnalyzer()
    try:
        stats = analyzer.my_analysis()
        with open('attach_stats.csv', mode='w') as file:
            writer = csv.writer(file)
            writer.writerow(["Input File Path", "Auth Requests", "Security Commands", "Attach Accepts", "Attach Requests", "Attach Rejections"])
            writer.writerow(["./logs/", stats["auth_requests"], stats["security_commands"], stats["attach_accepts"], stats["attach_requests"], stats["attach_rejections"]])
        print("Analysis completed successfully. Statistics saved in attach_stats.csv.")
    except Exception as e:
        print("Analysis failed. Error: {}".format(e))