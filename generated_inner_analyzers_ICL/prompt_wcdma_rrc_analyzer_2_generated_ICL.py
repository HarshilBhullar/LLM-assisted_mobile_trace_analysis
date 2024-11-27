
#!/usr/bin/python
# Filename: modified_wcdma_rrc_analyzer.py
"""
A modified WCDMA RRC analyzer with adjusted metrics.
"""

import xml.etree.ElementTree as ET
from mobile_insight.analyzer.analyzer import *
from mobile_insight.analyzer.state_machine import *
from mobile_insight.analyzer.protocol_analyzer import *

__all__ = ["ModifiedWcdmaRrcAnalyzer"]

class ModifiedWcdmaRrcAnalyzer(ProtocolAnalyzer):
    """
    A protocol analyzer for WCDMA (3G) Radio Resource Control (RRC) protocol with modified metrics.
    """

    def __init__(self):
        ProtocolAnalyzer.__init__(self)

        # Initialize packet filters
        self.add_source_callback(self.__rrc_filter)

        # Initialize internal states
        self.__status = WcdmaRrcStatus()  # Current cell status
        self.__history = {}  # Cell history: timestamp -> WcdmaRrcStatus()
        self.__config = {}  # cell_id -> WcdmaRrcConfig()
        self.state_machine = self.create_state_machine()

        # Temporary structure for holding the config
        self.__config_tmp = WcdmaRrcConfig()

    def set_source(self, source):
        """
        Set the trace source. Enable the WCDMA RRC messages.

        :param source: the trace source.
        """
        Analyzer.set_source(self, source)
        source.enable_log("WCDMA_RRC_OTA_Packet")
        source.enable_log("WCDMA_RRC_Serv_Cell_Info")
        source.enable_log("WCDMA_RRC_States")

    def create_state_machine(self):
        """
        Declare a RRC state machine

        returns: a StateMachine
        """
        def to_cell_fach(msg):
            return msg.type_id == "WCDMA_RRC_States" and str(msg.data['RRC State']) == 'CELL_FACH'

        def to_cell_dch(msg):
            return msg.type_id == "WCDMA_RRC_States" and str(msg.data['RRC State']) == 'CELL_DCH'

        def to_ura_pch(msg):
            return msg.type_id == "WCDMA_RRC_States" and str(msg.data['RRC State']) == 'URA_PCH'

        def to_cell_pch(msg):
            return msg.type_id == "WCDMA_RRC_States" and str(msg.data['RRC State']) == 'CELL_PCH'

        def to_idle(msg):
            return msg.type_id == "WCDMA_RRC_States" and str(msg.data['RRC State']) == 'DISCONNECTED'

        def init_state(msg):
            if msg.type_id == "WCDMA_RRC_States":
                return 'IDLE' if str(msg.data['RRC State']) == 'DISCONNECTED' else str(msg.data['RRC State'])

        rrc_state_machine = {
            'URA_PCH': {'CELL_FACH': to_cell_fach, 'CELL_DCH': to_cell_dch},
            'CELL_PCH': {'CELL_FACH': to_cell_fach},
            'CELL_DCH': {'URA_PCH': to_ura_pch, 'CELL_PCH': to_cell_pch, 'CELL_FACH': to_cell_fach, 'IDLE': to_idle},
            'CELL_FACH': {'URA_PCH': to_ura_pch, 'CELL_PCH': to_cell_pch, 'CELL_DCH': to_cell_dch, 'IDLE': to_idle},
            'IDLE': {'CELL_DCH': to_cell_dch, 'CELL_FACH': to_cell_fach}
        }

        return StateMachine(rrc_state_machine, init_state)

    def __rrc_filter(self, msg):
        """
        Filter all WCDMA RRC packets, and call functions to process it

        :param msg: the event (message) from the trace collector.
        """
        if msg.type_id == "WCDMA_RRC_Serv_Cell_Info":
            log_item = msg.data.decode()
            log_item_dict = dict(log_item)
            self.__callback_serv_cell(Event(msg.timestamp, msg.type_id, log_item_dict))

        elif msg.type_id == "WCDMA_RRC_States":
            log_item = msg.data.decode()
            log_item_dict = dict(log_item)
            self.__callback_rrc_state(log_item_dict)
            raw_msg = Event(msg.timestamp, msg.type_id, log_item_dict)
            if self.state_machine.update_state(raw_msg):
                self.log_info("Modified WCDMA state: " + self.state_machine.get_current_state())

        elif msg.type_id == "WCDMA_RRC_OTA_Packet":
            log_item = msg.data.decode()
            log_item_dict = dict(log_item)
            if 'Msg' in log_item_dict:
                log_xml = ET.XML(log_item_dict['Msg'])
                self.__callback_sib_config(Event(msg.timestamp, msg.type_id, log_xml))
                self.send(Event(msg.timestamp, msg.type_id, log_xml))

    def __callback_rrc_state(self, msg):
        rrc_state = {
            'RRC State': str(msg['RRC State']),
            'Timestamp': str(msg['timestamp'])
        }
        self.broadcast_info('MODIFIED_RRC_STATE', rrc_state)

    def __callback_serv_cell(self, msg):
        """
        A callback to update current cell status

        :param msg: the RRC messages with cell status
        """
        status_updated = False
        if not self.__status.inited():
            self.__status.freq = msg.data['Download RF channel number']
            self.__status.id = msg.data['Cell ID']
            self.__status.lac = msg.data['LAC']
            self.__status.rac = msg.data['RAC']
            status_updated = True
        else:
            if (self.__status.freq != msg.data['Download RF channel number'] or
                self.__status.id != msg.data['Cell ID'] or
                self.__status.lac != msg.data['LAC'] or
                self.__status.rac != msg.data['RAC']):
                
                self.__status = WcdmaRrcStatus()
                self.__status.freq = msg.data['Download RF channel number']
                self.__status.id = msg.data['Cell ID']
                self.__status.lac = msg.data['LAC']
                self.__status.rac = msg.data['RAC']
                self.__history[msg.timestamp] = self.__status
                self.__config_tmp = WcdmaRrcConfig()
                status_updated = True

        if status_updated:
            self.log_info(self.__status.dump())

    def __callback_sib_config(self, msg):
        """
        A callback to extract configurations from System Information Blocks (SIBs).

        :param msg: RRC SIB messages
        """
        for field in msg.data.iter('field'):
            if field.get('name') == "rrc.cellIdentity":
                cellId = int(field.get('value')[0:-1], 16)
                if not self.__status.inited():
                    self.__status.id = cellId
                    if self.__status.inited():
                        cur_pair = (self.__status.id, self.__status.freq)
                        self.__config[cur_pair] = self.__config_tmp
                        self.__config[cur_pair].__status = self.__status
                elif self.__status.id != cellId:
                    self.__status = WcdmaRrcStatus()
                    self.__status.id = cellId
                    self.__history[msg.timestamp] = self.__status
                    self.__config_tmp = WcdmaRrcConfig()

            # Additional processing for SIB configurations can be implemented here.

    def get_cell_list(self):
        """
        Get a complete list of cell IDs.

        :returns: a list of cells the device has associated with
        """
        return list(self.__config.keys())

    def get_cell_config(self, cell):
        """
        Return a cell's active/idle-state configuration.

        :param cell: a cell identifier
        :returns: this cell's active/idle-state configurations
        """
        return self.__config.get(cell, None)

    def get_cur_cell(self):
        """
        Get current cell's status

        :returns: current cell's status
        """
        return self.__status

    def get_cur_cell_config(self):
        """
        Get current cell's configuration

        :returns: current cell's configuration
        """
        cur_pair = (self.__status.id, self.__status.freq)
        return self.__config.get(cur_pair, None)

    def create_profile_hierarchy(self):
        """
        Return a WCDMA RRC ProfileHierarchy (configurations)

        :returns: ProfileHierarchy for WCDMA RRC
        """
        profile_hierarchy = ProfileHierarchy('ModifiedWcdmaRrcProfile')
        root = profile_hierarchy.get_root()
        status = root.add('status', False)  # Metadata
        sib = root.add('idle', False)  # Idle-state configurations
        active = root.add('active', False)  # Active-state configurations

        # Status metadata
        status.add('cell_id', False)
        status.add('freq', False)
        status.add('radio_technology', False)
        status.add('routing_area_code', False)
        status.add('location_area_code', False)
        status.add('bandwidth', False)
        status.add('conn_state', False)

        # Idle-state configurations
        sib_serv = sib.add('serv_config', False)  # Configuration as the serving cell
        intra_freq_config = sib.add('intra_freq_config', False)  # Intra-frequency handoff config
        inter_freq_config = sib.add('inter_freq_config', True)  # Inter-frequency/RAT handoff config

        sib_serv.add('priority', False)  # Cell reselection priority
        sib_serv.add('threshserv_low', False)  # Cell reselection threshold
        sib_serv.add('s_priority_search1', False)  # Searching other frequencies
        sib_serv.add('s_priority_search2', False)

        # Intra-frequency handoff parameter: frequency level
        intra_freq_config.add('tReselection', False)
        intra_freq_config.add('q_RxLevMin', False)
        intra_freq_config.add('s_InterSearch', False)
        intra_freq_config.add('s_IntraSearch', False)
        intra_freq_config.add('q_Hyst1', False)
        intra_freq_config.add('q_Hyst2', False)

        # Inter-frequency handoff parameter: frequency level
        inter_freq_config.add('rat', False)
        inter_freq_config.add('freq', False)
        inter_freq_config.add('tReselection', False)
        inter_freq_config.add('q_RxLevMin', False)
        inter_freq_config.add('p_Max', False)
        inter_freq_config.add('priority', False)
        inter_freq_config.add('threshx_high', False)
        inter_freq_config.add('threshx_low', False)

        return profile_hierarchy
