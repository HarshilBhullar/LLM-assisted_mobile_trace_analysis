
#!/usr/bin/python
# Filename: track_cell_info_analyzer_modified.py
"""
A modified analyzer to track cellular LTE RRC messages and extract cell information with additional metrics

Author: Assistant
"""

from mobile_insight.analyzer.analyzer import *

__all__ = ["TrackCellInfoAnalyzerModified"]

class TrackCellInfoAnalyzerModified(Analyzer):

    def __init__(self):
        Analyzer.__init__(self)

        self.add_source_callback(self.__msg_callback)

        self.cell_info = {
            'dl_freq': None,
            'ul_freq': None,
            'bandwidth': None,
            'cell_id': None,
            'tac': None,
            'operator': None,
            'allowed_access': None,
            'band_indicator': None,
            'avg_freq': None
        }

    def set_source(self, source):
        Analyzer.set_source(self, source)
        source.enable_log("LTE_RRC_Serv_Cell_Info")
        source.enable_log("LTE_RRC_MIB_Packet")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_RRC_Serv_Cell_Info":
            self.__process_serv_cell_info(msg)
        elif msg.type_id == "LTE_RRC_MIB_Packet":
            self.__process_mib_packet(msg)

    def __process_serv_cell_info(self, msg):
        log_item = msg.data.decode()
        self.cell_info['dl_freq'] = log_item.get('Downlink frequency')
        self.cell_info['ul_freq'] = log_item.get('Uplink frequency')
        self.cell_info['bandwidth'] = log_item.get('Bandwidth')
        self.cell_info['cell_id'] = log_item.get('Cell ID')
        self.cell_info['tac'] = log_item.get('TAC')
        self.cell_info['operator'] = log_item.get('Operator')
        self.cell_info['allowed_access'] = log_item.get('Allowed Access')
        self.cell_info['band_indicator'] = log_item.get('Band Indicator')
        self.cell_info['avg_freq'] = (self.cell_info['dl_freq'] + self.cell_info['ul_freq']) / 2 if self.cell_info['dl_freq'] and self.cell_info['ul_freq'] else None
        
        self.broadcast_info('CELL_INFO', self.cell_info)
        self.log_info("Updated cell info: " + str(self.cell_info))

    def __process_mib_packet(self, msg):
        log_item = msg.data.decode()
        mib_info = {
            'num_antennas': log_item.get('Number of Antennas'),
            'dl_bandwidth': log_item.get('Downlink Bandwidth'),
            'physical_cell_id': log_item.get('Physical Cell ID')
        }
        self.broadcast_info('MIB_INFO', mib_info)
        self.log_info("MIB info: " + str(mib_info))

    def get_current_cell_info(self):
        return self.cell_info

    def get_avg_freq(self):
        return self.cell_info['avg_freq']
