#!/usr/bin/python

import sys
import csv
import json

from mobile_insight.monitor import OfflineReplayer

__all__ = ["myNewAnalyzer"]

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from mobile_insight.analyzer.analyzer import *

class myNewAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)
        self.cell_status = {}
        self.kpi_values = {}

    def set_source(self, source):
        """
        Set the trace source. Enable the cellular signaling messages

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)
        source.enable_log("LTE_RRC_OTA_Packet")
        source.enable_log("LTE_NAS_EMM_OTA_Incoming_Packet")
        source.enable_log("LTE_NAS_EMM_OTA_Outgoing_Packet")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_RRC_OTA_Packet":
            self.__callback_serv_cell(msg)
        elif msg.type_id in ["LTE_NAS_EMM_OTA_Incoming_Packet", "LTE_NAS_EMM_OTA_Outgoing_Packet"]:
            self.__analyze_kpi(msg)

    def __callback_serv_cell(self, msg):
        """
        A callback to update current cell status
        :param msg: the RRC messages with cell status
        """
        data = msg.data.decode()
        if not self.cell_status.get('inited', False):
            self.cell_status['freq'] = data.get('Download RF channel number', 'None')
            self.cell_status['id'] = data.get('Cell ID', 'None')
            self.cell_status['lac'] = data.get('LAC', 'None')
            self.cell_status['rac'] = data.get('RAC', 'None')
            self.cell_status['inited'] = True

    def __analyze_kpi(self, msg):
        data = msg.data.decode()
        if 'Msg' in data.keys():
            log_xml = ET.XML(data['Msg'])
            xml_msg = Event(msg.timestamp, msg.type_id, log_xml)
            for field in xml_msg.data.iter('field'):
                if field.get('name') and 'nas_eps.nas_msg' in field.get('name'):
                    if field.get('showname') == 'NAS EPS Mobility Management Message Type: Attach request (0x41)':
                        self.kpi_values[msg.timestamp] = 'Attach Request Detected'

def my_analysis(input_path):

    src = OfflineReplayer()
    src.set_input_path(input_path)

    analyzer = myNewAnalyzer()
    analyzer.set_source(src)
    try:
        src.run()
    except:
        print('Failed:', input_path)
        return None

    return analyzer


input_path = sys.argv[1]
analyzer = my_analysis(input_path)
if analyzer:
    with open('cell_kpi_stats.json', 'a') as f:
        output = {
            "input_path": input_path,
            "cell_status": analyzer.cell_status,
            "kpi_values": analyzer.kpi_values
        }
        json.dump(output, f)
        f.write("\n")

### Explanation:
# - **Analyzer Initialization**: The `myNewAnalyzer` class inherits from `Analyzer` and initializes a callback for message handling. It maintains two dictionaries: `cell_status` to store the current cell configuration and `kpi_values` to log key performance indicators.

# - **Setting Source**: The `set_source` method enables specific logs for RRC and NAS messages, essential for capturing cell status and NAS signaling.

# - **Message Callback**:
#   - **Cell Status Update**: The `__callback_serv_cell` function updates the cell status with key parameters like frequency, cell ID, LAC, and RAC if not already initialized.
#   - **KPI Analysis**: The `__analyze_kpi` function inspects NAS messages, particularly looking for 'Attach Request' messages and logs them with a timestamp.

# - **Output**: The results are written to a JSON file `cell_kpi_stats.json`, capturing both cell status and KPI values, providing a comprehensive view of the analyzed data.