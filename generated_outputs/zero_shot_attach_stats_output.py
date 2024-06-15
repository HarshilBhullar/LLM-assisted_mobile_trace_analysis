
from mobile_insight.analyzer import Analyzer
from mobile_insight.analyzer.analyzer import OfflineReplayer
import csv

class myAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.auth_req_count = 0
        self.security_cmd_count = 0
        self.attach_accept_count = 0
        self.attach_req_count = 0
        self.attach_reject_count = 0

    def __msg_callback(self, msg):
        # Process each message and update counters
        if msg.type_id == "nas_5gsa_emm_message":
            if msg.HasField("attach_request"):
                self.attach_req_count += 1
            elif msg.HasField("attach_accept"):
                self.attach_accept_count += 1
            elif msg.HasField("attach_reject"):
                self.attach_reject_count += 1
        elif msg.type_id == "nas_5gsa_esm_message":
            if msg.HasField("ue_security_mode_command"):
                self.security_cmd_count += 1
            elif msg.HasField("authentication_request"):
                self.auth_req_count += 1

def my_analysis(input_path):
    try:
        source = OfflineReplayer()
        source.set_input_path(input_path)
        analyzer = myAnalyzer()
        source.add_analyzer(analyzer)
        source.run()

        counts = [analyzer.auth_req_count, analyzer.security_cmd_count, analyzer.attach_accept_count, analyzer.attach_req_count, analyzer.attach_reject_count]

        with open('attach_stats.csv', mode='a') as file:
            writer = csv.writer(file)
            writer.writerow([input_path] + counts)

    except Exception as e:
        print("Analysis failed: {}".format(e))

if __name__ == "__main__":
    input_path = "path/to/trace_logs.mi2log"  # Update with the actual path to the trace logs
    my_analysis(input_path)
