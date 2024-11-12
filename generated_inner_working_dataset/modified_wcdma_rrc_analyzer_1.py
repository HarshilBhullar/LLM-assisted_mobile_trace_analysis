
#!/usr/bin/python
# Filename: modified_wcdma_rrc_analyzer.py
"""
A modified WCDMA (3G) RRC analyzer with adjusted metrics.

Author: Yuanjie Li, Zhehui Zhang, Modified by [Your Name]
"""

import xml.etree.ElementTree as ET
from .analyzer import *
from .state_machine import *
from .protocol_analyzer import *
import timeit

from .profile import Profile,ProfileHierarchy

__all__=["ModifiedWcdmaRrcAnalyzer"]

class ModifiedWcdmaRrcAnalyzer(ProtocolAnalyzer):

    """
    A protocol analyzer for WCDMA (3G) Radio Resource Control (RRC) protocol with modified metrics.
    """

    def __init__(self):

        ProtocolAnalyzer.__init__(self)

        #init packet filters
        self.add_source_callback(self.__rrc_filter)

        #init internal states
        self.__status=WcdmaRrcStatus()    # current cell status
        self.__history={}    # cell history: timestamp -> WcdmaRrcStatus()
        self.__config={}    # cell_id -> WcdmaRrcConfig()
        self.state_machine = self.create_state_machine()

        #FIXME: change the timestamp
        self.__history[0]=self.__config

        #Temporary structure for holding the config
        self.__config_tmp=WcdmaRrcConfig()

    def set_source(self,source):
        """
        Set the trace source. Enable the WCDMA RRC messages.

        :param source: the trace source.
        :type source: trace collector
        """
        Analyzer.set_source(self,source)
        #enable WCDMA RRC log
        source.enable_log("WCDMA_RRC_OTA_Packet")
        source.enable_log("WCDMA_RRC_Serv_Cell_Info")
        source.enable_log("WCDMA_RRC_States")

    def create_state_machine(self):
        """
        Declare a RRC state machine

        returns: a StateMachine
        """

        def to_cell_fach(msg):
            if msg.type_id == "WCDMA_RRC_States" and str(msg.data['RRC State']) == 'CELL_FACH':
                return True

        def to_cell_dch(msg):
            if msg.type_id == "WCDMA_RRC_States" and str(msg.data['RRC State']) == 'CELL_DCH':
                return True

        def to_ura_pch(msg):
            if msg.type_id == "WCDMA_RRC_States" and str(msg.data['RRC State']) == 'URA_PCH':
                return True

        def to_cell_pch(msg):
            if msg.type_id == "WCDMA_RRC_States" and str(msg.data['RRC State']) == 'CELL_PCH':
                return True

        def to_idle(msg):
            if msg.type_id == "WCDMA_RRC_States" and str(msg.data['RRC State']) == 'DISCONNECTED':
                return True

        def init_state(msg):
            if msg.type_id == "WCDMA_RRC_States":
                state = 'IDLE' if str(msg.data['RRC State']) == 'DISCONNECTED' else str(msg.data['RRC State'])
                return state

        rrc_state_machine={'URA_PCH': {'CELL_FACH': to_cell_fach, 'CELL_DCH': to_cell_dch},
                       'CELL_PCH': {'CELL_FACH': to_cell_fach},
                       'CELL_DCH': {'URA_PCH': to_ura_pch, 'CELL_PCH': to_cell_pch, 'CELL_FACH': to_cell_fach, 'IDLE': to_idle},
                       'CELL_FACH': {'URA_PCH': to_ura_pch, 'CELL_PCH': to_cell_pch, 'CELL_DCH': to_cell_dch, 'IDLE': to_idle},
                       'IDLE': {'CELL_DCH': to_cell_dch, 'CELL_FACH': to_cell_fach}}

        return StateMachine(rrc_state_machine, init_state)

    def __rrc_filter(self,msg):
        
        """
        Filter all WCDMA RRC packets, and call functions to process it

        :param msg: the event (message) from the trace collector.
        """

        if msg.type_id == "WCDMA_RRC_Serv_Cell_Info":

            log_item = msg.data.decode()
            log_item_dict = dict(log_item)
            raw_msg=Event(msg.timestamp,msg.type_id,log_item_dict)
            self.__callback_serv_cell(raw_msg)

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
            log_xml = None
            if 'Msg' in log_item_dict:
                log_xml = ET.XML(log_item_dict['Msg'])
            else:
                return

            xml_msg=Event(msg.timestamp,msg.type_id,log_xml)

            self.__callback_sib_config(xml_msg)
            self.send(xml_msg) #deliver WCDMA signaling messages only (decoded)

    def __callback_rrc_state(self,msg):
        rrc_state = {}
        rrc_state['RRC State'] = str(msg['RRC State'])
        rrc_state['Timestamp'] = str(msg['timestamp'])
        self.broadcast_info('MODIFIED_RRC_STATE',rrc_state)

    def __callback_serv_cell(self,msg):
        """
        A callback to update current cell status

        :param msg: the RRC messages with cell status
        """
        status_updated = False
        if not self.__status.inited():
            self.__status.freq=msg.data['Download RF channel number']
            self.__status.id=msg.data['Cell ID']
            self.__status.lac=msg.data['LAC']
            self.__status.rac=msg.data['RAC']
            status_updated = True

        else:
            if self.__status.freq!=msg.data['Download RF channel number'] \
            or self.__status.id!=msg.data['Cell ID'] \
            or self.__status.lac!=msg.data['LAC'] \
            or self.__status.rac!=msg.data['RAC']:
                self.__status=WcdmaRrcStatus()
                self.__status.freq=msg.data['Download RF channel number']
                self.__status.id=msg.data['Cell ID']
                self.__status.lac=msg.data['LAC']
                self.__status.rac=msg.data['RAC']
                self.__history[msg.timestamp]=self.__status
                self.__config_tmp=WcdmaRrcConfig()

                status_updated = True

        if status_updated:
            self.log_info(self.__status.dump())

    def __callback_sib_config(self,msg):
        """
        A callback to extract configurations from System Information Blocks (SIBs), 
        including the radio assessment thresholds, the preference settings, etc.

        :param msg: RRC SIB messages
        """

        for field in msg.data.iter('field'):

            if field.get('name') == "rrc.cellIdentity":
                cellId = int(field.get('value')[0:-1],16)
                if not self.__status.inited():
                    self.__status.id = cellId
                    if self.__status.inited():
                        cur_pair = (self.__status.id,self.__status.freq)
                        self.__config[cur_pair] = self.__config_tmp
                        self.__config[cur_pair].__status = self.__status
                elif self.__status.id != cellId:
                    self.__status = WcdmaRrcStatus()
                    self.__status.id = cellId
                    self.__history[msg.timestamp] = self.__status
                    self.__config_tmp = WcdmaRrcConfig()

            if field.get('name') == "rrc.utra_ServingCell_element": 
                field_val = {}

                field_val['rrc.priority'] = None    #mandatory
                field_val['rrc.threshServingLow'] = None    #mandatory
                field_val['rrc.s_PrioritySearch1'] = None    #mandatory
                field_val['rrc.s_PrioritySearch2'] = 0    #optional

                for val in field.iter('field'):
                    field_val[val.get('name')] = val.get('show')

                serv_config = WcdmaRrcSibServ(
                    int(field_val['rrc.priority']),
                    int(field_val['rrc.threshServingLow'])*3,  # Modified threshold
                    int(field_val['rrc.s_PrioritySearch1'])*3,  # Modified search priority
                    int(field_val['rrc.s_PrioritySearch2']))
                
                if not self.__status.inited():
                    self.__config_tmp.sib.serv_config = serv_config
                else:
                    cur_pair = (self.__status.id,self.__status.freq)
                    if cur_pair not in self.__config:
                        self.__config[cur_pair] = WcdmaRrcConfig()
                        self.__config[cur_pair].status=self.__status

                    self.__config[cur_pair].sib.serv_config = serv_config

                if self.__status.inited():
                    self.profile.update("ModifiedWcdmaRrcProfile:"+str(self.__status.id)+"_"+str(self.__status.freq)+".idle.serv_config",
                        {'priority':field_val['rrc.priority'],
                         'threshserv_low':str(int(field_val['rrc.threshServingLow'])*3),
                         's_priority_search1':str(int(field_val['rrc.s_PrioritySearch1'])*3),
                         's_priority_search2':field_val['rrc.s_PrioritySearch2']
                         })

            if field.get('name') == "rrc.cellSelectReselectInfo_element":
                field_val = {}

                field_val['rrc.s_Intrasearch'] = 0
                field_val['rrc.s_Intersearch'] = 0
                field_val['rrc.q_RxlevMin'] = None #mandatory
                field_val['rrc.q_QualMin'] = None #mandatory
                field_val['rrc.q_Hyst_l_S'] = None #mandatory
                field_val['rrc.t_Reselection_S'] = None #mandatory
                field_val['rrc.q_HYST_2_S'] = None #optional, default=q_Hyst_l_S

                for val in field.iter('field'):
                    field_val[val.get('name')] = val.get('show')

                if not field_val['rrc.q_Hyst_l_S']:
                    field_val['rrc.q_Hyst_l_S'] = 2

                if not field_val['rrc.q_HYST_2_S']:
                    field_val['rrc.q_HYST_2_S'] = field_val['rrc.q_Hyst_l_S']

                if not field_val['rrc.t_Reselection_S']:
                    field_val['rrc.t_Reselection_S'] = 0

                if not field_val['rrc.q_RxlevMin']:
                    field_val['rrc.q_RxlevMin'] = 0

                intra_freq_config = WcdmaRrcSibIntraFreqConfig(
                        int(field_val['rrc.t_Reselection_S']),
                        int(field_val['rrc.q_RxlevMin'])*3,  # Modified level minimum
                        int(field_val['rrc.s_Intersearch'])*3,  # Modified search
                        int(field_val['rrc.s_Intrasearch'])*3,
                        int(field_val['rrc.q_Hyst_l_S'])*3,
                        int(field_val['rrc.q_HYST_2_S'])*3)

                if not self.__status.inited():        
                    self.__config_tmp.sib.intra_freq_config = intra_freq_config
                else:
                    cur_pair = (self.__status.id,self.__status.freq)
                    if cur_pair not in self.__config:
                        self.__config[cur_pair] = WcdmaRrcConfig()
                        self.__config[cur_pair].status=self.__status
                    self.__config[cur_pair].sib.intra_freq_config = intra_freq_config

                if self.__status.inited():
                    self.profile.update("ModifiedWcdmaRrcProfile:"+str(self.__status.id)+"_"+str(self.__status.freq)+".idle.intra_freq_config",
                        {'tReselection':field_val['rrc.t_Reselection_S'],
                         'q_RxLevMin':str(int(field_val['rrc.q_RxlevMin'])*3),
                         's_InterSearch':str(int(field_val['rrc.s_Intrasearch'])*3),
                         's_IntraSearch':str(int(field_val['rrc.s_Intrasearch'])*3),
                         'q_Hyst1':str(int(field_val['rrc.q_Hyst_l_S'])*3),
                         'q_Hyst2':str(int(field_val['rrc.q_HYST_2_S'])*3)
                         })

            if field.get('name') == "rrc.EUTRA_FrequencyAndPriorityInfo_element":
                field_val = {}

                field_val['rrc.earfcn'] = None
                field_val['rrc.priority'] = None
                field_val['rrc.qRxLevMinEUTRA'] = -140
                field_val['rrc.threshXhigh'] = None
                field_val['rrc.threshXlow'] = None

                for val in field.iter('field'):
                    field_val[val.get('name')] = val.get('show')

                neighbor_freq = int(field_val['rrc.earfcn'])

                inter_freq_config=WcdmaRrcSibInterFreqConfig(
                                    neighbor_freq,
                                    None,
                                    int(field_val['rrc.qRxLevMinEUTRA'])*3,  # Modified level minimum
                                    None,
                                    int(field_val['rrc.priority']),
                                    int(field_val['rrc.threshXhigh'])*3,  # Modified threshold
                                    int(field_val['rrc.threshXlow'])*3)
                if not self.__status.inited():
                    self.__config_tmp.sib.inter_freq_config[neighbor_freq] = inter_freq_config
                else:
                    cur_pair = (self.__status.id,self.__status.freq)
                    if cur_pair not in self.__config:
                        self.__config[cur_pair] = WcdmaRrcConfig()
                        self.__config[cur_pair].status=self.__status
                    self.__config[cur_pair].sib.inter_freq_config[neighbor_freq] = inter_freq_config

                if self.__status.inited():
                    self.profile.update("ModifiedWcdmaRrcProfile:"+str(self.__status.id)+"_"+str(self.__status.freq)+".idle.inter_freq_config:"+str(neighbor_freq),
                        {'rat':'LTE',
                         'freq':str(neighbor_freq),
                         'tReselection':'null',
                         'q_RxLevMin':str(int(field_val['rrc.qRxLevMinEUTRA'])*3),
                         'p_Max':'null',
                         'priority':field_val['rrc.priority'],
                         'threshx_high':str(int(field_val['rrc.threshXhigh'])*3),
                         'threshx_low':str(int(field_val['rrc.threshXlow'])*3)
                         })

    def get_cell_list(self):
        """
        Get a complete list of cell IDs.

        :returns: a list of cells the device has associated with
        """
        return list(self.__config.keys())

    def get_cell_config(self,cell):
        """
        Return a cell's active/idle-state configuration.
        
        :param cell:  a cell identifier
        :type cell: a (cell_id,freq) pair
        :returns: this cell's active/idle-state configurations
        :rtype: WcdmaRrcConfig
        """
        if cell in self.__config:
            return self.__config[cell]
        else:
            return None

    def get_cur_cell(self):
        """
        Get current cell's status

        :returns: current cell's status
        :rtype: WcdmaRrcStatus      
        """
        return self.__status

    def get_cur_cell_config(self):
        """
        Get current cell's configuration

        :returns: current cell's status
        :rtype: WcdmaRrcConfig
        """
        cur_pair = (self.__status.id,self.__status.freq)
        if cur_pair in self.__config:
            return self.__config[cur_pair]
        else:
            return None

    def create_profile_hierarchy(self):

        '''
        Return a Wcdma Rrc ProfileHierarchy (configurations)

        :returns: ProfileHierarchy for WCDMA RRC
        '''
        
        profile_hierarchy = ProfileHierarchy('ModifiedWcdmaRrcProfile')
        root = profile_hierarchy.get_root()
        status = root.add('status',False) #metadata
        sib = root.add('idle',False) #Idle-state configurations
        active = root.add('active',False) #Active-state configurations

        #Status metadata
        status.add('cell_id',False)
        status.add('freq',False)
        status.add('radio_technology',False)
        status.add('routing_area_code',False)
        status.add('location_area_code',False)
        status.add('bandwidth',False)
        status.add('conn_state',False)

        #Idle-state configurations
        sib_serv = sib.add('serv_config',False) #configuration as the serving cell
        intra_freq_config = sib.add('intra_freq_config',False) #Intra-frequency handoff config
        inter_freq_config = sib.add('inter_freq_config',True) #Inter-frequency/RAT handoff config

        sib_serv.add('priority',False) #cell reselection priority
        sib_serv.add('threshserv_low',False) #cell reselection threshold
        sib_serv.add('s_priority_search1',False) #searching other frequencies
        sib_serv.add('s_priority_search2',False)

        #Intra-frequency handoff parameter: frequency level
        intra_freq_config.add('tReselection',False)
        intra_freq_config.add('q_RxLevMin',False)
        intra_freq_config.add('s_InterSearch',False)
        intra_freq_config.add('s_IntraSearch',False)
        intra_freq_config.add('q_Hyst1',False)
        intra_freq_config.add('q_Hyst2',False)

        #Inter-frequency handoff parameter: frequency level
        inter_freq_config.add('rat',False)
        inter_freq_config.add('freq',False)
        inter_freq_config.add('tReselection',False)
        inter_freq_config.add('q_RxLevMin',False)
        inter_freq_config.add('p_Max',False)
        inter_freq_config.add('priority',False)
        inter_freq_config.add('threshx_high',False)
        inter_freq_config.add('threshx_low',False)

        return profile_hierarchy

    def init_protocol_state(self, msg):
        """
        Determine RRC state at bootstrap

        :returns: current RRC state, or None if not determinable 
        """
        for field in msg.data.iter('field'):
            if field.get('name') == "rrc.rrcConnectionSetup" \
            or field.get('name') == "rrc.radioBearerReconfiguration" \
            or field.get('name') == "rrc.measurementReport_element":
                return 'RRC_DCH'
            elif field.get('name') == "rrc.rrcConnectionRelease":
                return 'RRC_IDLE'
        return None
