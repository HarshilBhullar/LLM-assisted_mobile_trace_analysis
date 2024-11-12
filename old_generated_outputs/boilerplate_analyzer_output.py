import sys
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import LteRrcAnalyzer

if __name__ == "__main__":
    src = OfflineReplayer()
    src.set_input_path(sys.argv[1])
    
    rrc_analyzer = LteRrcAnalyzer()
    rrc_analyzer.set_source(src)
    src.run()

    # Dictionary to keep track of MCC/MNC changes per minute
    mcc_mnc_changes_per_minute = {}

    for mcc_mnc_change in rrc_analyzer.rrc_mcc_mnc_changes:
        timestamp_minute = int(mcc_mnc_change['timestamp'].timestamp() // 60)
        if timestamp_minute in mcc_mnc_changes_per_minute:
            mcc_mnc_changes_per_minute[timestamp_minute] += 1
        else:
            mcc_mnc_changes_per_minute[timestamp_minute] = 1

    for minute, changes in mcc_mnc_changes_per_minute.items():
        print("Minute:", minute, "- MCC/MNC changes occurred:", changes)