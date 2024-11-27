
#!/usr/bin/python
# Filename: modified_lte_rrc_analyzer.py
"""
A modified LTE RRC analyzer with adjusted metrics for demonstration.
Author: Adapted from Yuanjie Li, Zhehui Zhang
"""

import xml.etree.ElementTree as ET
from .analyzer import *
from .state_machine import *
from .protocol_analyzer import *
import timeit
import time

from .profile import Profile, ProfileHierarchy

__all__ = ["ModifiedLteRrcAnalyzer"]

# Q-offset range mapping (6.3.4, TS36.331)
q_offset_range = {
    0: -24, 1: -22, 2: -20, 3: -18, 4: -16, 5: -14,
    6: -12, 7: -10, 8: -8, 9: -6, 10: -5, 11: -4,
    12: -3, 13: -2, 14: -1, 15: 0, 16: 1, 17: 2,
    18: 3, 19: 4, 20: 5, 21: 6, 22: 8, 23: 10, 24: 12,
    25: 14, 26: 16, 27: 18, 28: 20, 29: 22, 30: 24
}


class ModifiedLteRrcAnalyzer(ProtocolAnalyzer):
    """
    A modified protocol analyzer for LTE Radio Resource Control (RRC) protocol.
    """

    def __init__(self):
        print("Init Modified RRC Analyzer")
        ProtocolAnalyzer.__init__(self)
        self.state_machine = self.create_state_machine()

        # init packet filters
        self.add_source_callback(self.__rrc_filter)

        # init internal states
        self.__status = LteRrcStatus()  # current cell status
        self.__history = {}  # cell history: timestamp -> LteRrcStatus()
        self.__config = {}  # (cell_id,freq) -> LteRrcConfig()

    def create_profile_hierarchy(self):
        '''
        Return a Lte Rrc ProfileHierarchy (configurations)

        :returns: ProfileHierarchy for LTE RRC
        '''

        profile_hierarchy = ProfileHierarchy('LteRrcProfile')
        root = profile_hierarchy.get_root()
        status = root.add('status', False)  # metadata
        sib = root.add('idle', False)  # Idle-state configurations
        active = root.add('active', False)  # Active-state configurations

        # Status metadata
        status.add('cell_id', False)
        status.add('freq', False)
        status.add('radio_technology', False)
        status.add('tracking_area_code', False)
        status.add('bandwidth', False)
        status.add('conn_state', False)

        # Idle-state configurations
        sib_serv = sib.add('serv_config', False)  # configuration as the serving cell
        # Per-frequency configurations
        intra_freq_config = sib.add('intra_freq_config', False)  # Intra-frequency handoff config
        # TODO: for inter-freq/RAT, should have a mapping from freq/RAT to config
        inter_freq_config = sib.add('inter_freq_config', True)  # Inter-frequency/RAT handoff config
        intra_freq_cell_config = sib.add('intra_freq_cell_config', True)  # per-cell offsets for intra-freq
        inter_freq_cell_config = sib.add('inter_freq_cell_config', True)  # per-cell offsets for inter-freq

        sib_serv.add('priority', False)  # cell reselection priority
        sib_serv.add('threshserv_low', False)  # cell reselection threshold
        sib_serv.add('s_nonintrasearch', False)  # threshold for searching other frequencies
        sib_serv.add('q_hyst', False)

        # Intra-frequency handoff parameter: frequency level
        intra_freq_config.add('tReselection', False)
        intra_freq_config.add('q_RxLevMin', False)
        intra_freq_config.add('p_Max', False)
        intra_freq_config.add('s_IntraSearch', False)

        # Inter-frequency handoff parameter: frequency level
        inter_freq_config.add('rat', False)
        inter_freq_config.add('freq', False)
        inter_freq_config.add('tReselection', False)
        inter_freq_config.add('q_RxLevMin', False)
        inter_freq_config.add('p_Max', False)
        inter_freq_config.add('priority', False)
        inter_freq_config.add('threshx_high', False)
        inter_freq_config.add('threshx_low', False)
        inter_freq_config.add('q_offset_freq', False)

        # Intra/inter-frequency parameter: per-cell level
        intra_freq_cell_config.add('offset', False)
        inter_freq_cell_config.add('offset', False)

        # Active-state configuration
        meas_obj = active.add('meas_obj', True)  # freq->measobject
        report_list = active.add('report_list', True)  # report_id->reportConfig
        measid_list = active.add('measid_list', True)  # meas_id->(obj_id,report_id)

        # measurement object
        meas_obj.add('obj_id', False)  # meas object ID
        meas_obj.add('freq', False)  # carrier frequency
        meas_obj.add('offset_freq', False)  # frequency-specific measurement offset
        individual_offset = meas_obj.add('offset', True)  # cellID->cellIndividualOffset
        individual_offset.add('offset', False)
        # TODO: add cell blacklist

        report_list.add('id', False)  # report ID
        report_list.add('hyst', False)  # Hysteresis
        event = report_list.add('report_event', True)  # report event: eventID->thresholds
        event.add('event_type', False)
        event.add('threshold_1', False)
        event.add('threshold_2', False)

        # measurement id
        measid_list.add('obj_id', False)
        measid_list.add('report_id', False)

        return profile_hierarchy

    def create_state_machine(self):
        """
        Declare a RRC state machine

        returns: a StateMachine
        """

        def idle_to_crx(msg):
            if msg.type_id == "LTE_RRC_OTA_Packet":
                for field in msg.data.iter('field'):
                    if field.get('name') == "lte-rrc.rrcConnectionSetupComplete_element":
                        return True

        def crx_to_sdrx(msg):
            if msg.type_id == "LTE_RRC_CDRX_Events_Info":
                if msg.data['CDRX Event'] == "SHORT_CYCLE_START":
                    return True

        def crx_to_ldrx(msg):
            if msg.type_id == "LTE_RRC_CDRX_Events_Info":
                if msg.data['CDRX Event'] == "LONG_CYCLE_START":
                    return True

        def crx_to_idle(msg):
            if msg.type_id == "LTE_RRC_OTA_Packet":
                for field in msg.data.iter('field'):
                    if field.get('name') == "lte-rrc.rrcConnectionRelease_element":
                        return True

        def sdrx_to_ldrx(msg):
            if msg.type_id == "LTE_RRC_CDRX_Events_Info":
                if msg.data['CDRX Event'] == "LONG_CYCLE_START":
                    return True

        def sdrx_to_crx(msg):
            if msg.type_id == "LTE_RRC_CDRX_Events_Info":
                if msg.data['CDRX Event'] == "INACTIVITY_TIMER_START" or msg.data[
                    'CDRX Event'] == "INACTIVITY_TIMER_END":
                    return True

        def ldrx_to_crx(msg):
            if msg.type_id == "LTE_RRC_CDRX_Events_Info":
                if msg.data['CDRX Event'] == "INACTIVITY_TIMER_START" or msg.data[
                    'CDRX Event'] == "INACTIVITY_TIMER_END":
                    return True

        state_machine = {'RRC_IDLE': {'RRC_CRX': idle_to_crx},
                         'RRC_CRX': {'RRC_SDRX': crx_to_sdrx, 'RRC_LDRX': crx_to_ldrx, 'RRC_IDLE': crx_to_idle},
                         'RRC_SDRX': {'RRC_LDRX': sdrx_to_ldrx, 'RRC_CRX': sdrx_to_crx},
                         'RRC_LDRX': {'RRC_CRX': ldrx_to_crx}}

        return StateMachine(state_machine, self.init_protocol_state)

    def init_protocol_state(self, msg):
        """
        Determine RRC state at bootstrap

        :returns: current RRC state, or None if not determinable
        """
        if msg.type_id == "LTE_RRC_OTA_Packet":
            for field in msg.data.iter('field'):
                if field.get('name') == "lte-rrc.rrcConnectionSetupComplete_element" \
                        or field.get('name') == "lte-rrc.rrcConnectionReconfiguration_element":
                    return 'RRC_CRX'
                elif field.get('name') == "lte-rrc.rrcConnectionRelease_element":
                    return 'RRC_IDLE'
        elif msg.type_id == "LTE_RRC_CDRX_Events_Info":
            if msg.data['CDRX Event'] == "INACTIVITY_TIMER_START" or msg.data['CDRX Event'] == "INACTIVITY_TIMER_END":
                return 'RRC_CRX'
            elif msg.data['CDRX Event'] == "LONG_CYCLE_START":
                return 'RRC_LDRX'
            elif msg.data['CDRX Event'] == "SHORT_CYCLE_START":
                return 'RRC_SDRX'
        return None

    def __rrc_filter(self, msg):

        """
        Filter all LTE RRC packets, and call functions to process it

        :param msg: the event (message) from the trace collector.
        """
        # log_item = msg.data
        log_item = msg.data.decode()
        log_item_dict = dict(log_item)

        self.send_to_coordinator(Event(msg.timestamp, msg.type_id, str(log_item)))

        # Calllbacks triggering
        if msg.type_id == "LTE_RRC_OTA_Packet":

            if 'Msg' not in log_item_dict:
                return

            # Convert msg to xml format
            # log_xml = ET.fromstring(log_item_dict['Msg'])
            log_xml = ET.XML(log_item_dict['Msg'])
            # print xml_log
            # print str(log_item_dict)
            # xml_msg = Event(msg.timestamp,msg.type_id,log_xml)
            xml_msg = Event(log_item_dict['timestamp'], msg.type_id, log_xml)

            if self.state_machine.update_state(xml_msg):
                # self.log_info("rrc state: " + str(self.state_machine.get_current_state()))
                event = Event(msg.timestamp, 'rrc state', str(self.state_machine.get_current_state()))
                self.send_to_coordinator(event)

            tic = time.process_time()
            self.__callback_rrc_conn(xml_msg)
            toc = time.process_time()

            # self.log_info(str(time.time()) + " "\
            #             + "CALLBK_LTE_RRC_CONN "\
            #             + str((toc - tic)*1000)) #processing latency (in ms)

            tic = time.process_time()
            self.__callback_sib_config(xml_msg)
            toc = time.process_time()

            # self.log_info(str(time.time()) + " "\
            #             + "CALLBK_LTE_RRC_SIB_CONFG "\
            #             + str((toc - tic)*1000)) #processing latency (in ms)


            tic = time.process_time()
            self.__callback_rrc_reconfig(xml_msg)
            toc = time.process_time()

            # self.log_info(str(time.time()) + " "\
            #             + "CALLBK_LTE_RRC_RECONFIG "\
            #             + str((toc - tic)*1000)) #processing latency (in ms)

            # TODO: callback RRC

            # Raise event to other analyzers
            # e = Event(timeit.default_timer(),self.__class__.__name__,"")
            # self.send(e)
            self.send(xml_msg)  # deliver LTE RRC signaling messages (decoded)
        elif msg.type_id == "LTE_RRC_Serv_Cell_Info":
            raw_msg = Event(msg.timestamp, msg.type_id, log_item_dict)
            self.__callback_serv_cell(raw_msg)
        elif msg.type_id == "LTE_RRC_CDRX_Events_Info":
            for item in log_item_dict['Records']:
                # print item
                raw_msg = Event(' '.join(map(str, [log_item_dict['timestamp'], item['SFN'], item['Sub-FN']])),
                                msg.type_id, item)
                if self.state_machine.update_state(raw_msg):
                    # self.log_info("rrc state: " + str(self.state_machine.get_current_state()))
                    event = Event(msg.timestamp, 'rrc state', str(self.state_machine.get_current_state()))
                    self.send_to_coordinator(event)
                    # self.log_info("rrc state history: " + str(self.state_machine.state_history))
            self.__callback_drx(log_item_dict)

    def __callback_drx(self, msg):

        # Broadcast to other apps
        drx_state = {}
        drx_state['Conn state'] = "CONNECTED"
        drx_state['Timestamp'] = str(msg['timestamp'])
        drx_transition = ""
        for item in msg['Records']:
            if item['CDRX Event'] == "INACTIVITY_TIMER_START":
                drx_state['DRX state'] = "CRX"
                self.broadcast_info('DRX', drx_state)
            elif item['CDRX Event'] == "INACTIVITY_TIMER_END":
                drx_state['DRX state'] = "CRX"
                self.broadcast_info('DRX', drx_state)
            elif item['CDRX Event'] == "LONG_CYCLE_START":
                drx_state['DRX state'] = "LONG_DRX"
                self.broadcast_info('DRX', drx_state)
            elif item['CDRX Event'] == "SHORT_CYCLE_START":
                drx_state['DRX state'] = "SHORT_DRX"
                self.broadcast_info('DRX', drx_state)

    def __callback_serv_cell(self, msg):

        """
        A callback to update current cell status

        :param msg: the RRC messages with cell status
        """
        status_updated = False
        if not self.__status.inited():
            status_updated = True
            self.__status.freq = msg.data['Downlink frequency']
            self.__status.id = msg.data['Cell ID']
            self.__status.tac = msg.data['TAC']

        else:
            if self.__status.freq != msg.data['Downlink frequency'] \
                    or self.__status.id != msg.data['Cell ID'] \
                    or self.__status.tac != msg.data['TAC']:
                status_updated = True
                curr_conn = self.__status.conn
                self.__status = LteRrcStatus()
                self.__status.conn = curr_conn
                self.__status.freq = msg.data['Downlink frequency']
                self.__status.id = msg.data['Cell ID']
                self.__status.tac = msg.data['TAC']
                self.__history[msg.timestamp] = self.__status

        if status_updated:
            self.log_info(self.__status.dump())
            self.broadcast_info('LTE_RRC_STATUS', self.__status.dump_dict())

    def __callback_sib_config(self, msg):
        """
        A callback to extract configurations from System Information Blocks (SIBs),
        including the radio asssement thresholds, the preference settings, etc.

        :param msg: RRC SIB messages
        """
        for field in msg.data.iter('field'):

            if field.get('name') == 'lte-rrc.measResultPCell_element':
                meas_report = {}
                meas_report['timestamp'] = str(msg.timestamp)
                for val in field.iter('field'):
                    if val.get('name') == 'lte-rrc.rsrpResult':
                        meas_report['rsrp'] = int(val.get('show'))
                        meas_report['rssi'] = meas_report['rsrp'] - 131  # map rsrp to rssi, altered calculation
                    elif val.get('name') == 'lte-rrc.rsrqResult':
                        meas_report['rsrq'] = int(val.get('show')) + 1  # adjusted rsrq calculation
                self.broadcast_info('MEAS_PCELL', meas_report)
                self.log_info('MEAS_PCELL: ' + str(meas_report))
                self.send_to_coordinator(Event(msg.timestamp, 'rsrp', meas_report['rsrp']))
                self.send_to_coordinator(Event(msg.timestamp, 'rsrq', meas_report['rsrq']))

            # TODO: use MIB, not lte-rrc.trackingAreaCode
            # if field.get('name') == "lte-rrc.trackingAreaCode":  # tracking area code
            #     self.__status.tac = int(field.get('show'))

            # serving cell and intra-frequency reselection info
            if field.get('name') == "lte-rrc.sib3_element":

                field_val = {}

                # Default value setting
                # FIXME: set default to those in TS36.331
                field_val['lte-rrc.cellReselectionPriority'] = 0  # mandatory
                field_val['lte-rrc.threshServingLow'] = 0  # mandatory
                field_val['lte-rrc.s_NonIntraSearch'] = "inf"
                field_val['lte-rrc.q_Hyst'] = 0
                field_val['lte-rrc.utra_q_RxLevMin'] = 0  # mandatory
                field_val['lte-rrc.p_Max'] = 23  # default value for UE category 3
                field_val['lte-rrc.s_IntraSearch'] = "inf"
                field_val['lte-rrc.t_ReselectionEUTRA'] = 0

                for val in field.iter('field'):
                    field_val[val.get('name')] = val.get('show')

                cur_pair = (self.__status.id, self.__status.freq)
                if cur_pair not in self.__config:
                    self.__config[cur_pair] = LteRrcConfig()
                    self.__config[cur_pair].status = self.__status

                self.__config[cur_pair].sib.serv_config = LteRrcSibServ(
                    int(field_val['lte-rrc.cellReselectionPriority']),
                    int(field_val['lte-rrc.threshServingLow']) * 2,
                    float(field_val['lte-rrc.s_NonIntraSearch']) * 2,
                    int(field_val['lte-rrc.q_Hyst']))

                # Test profile
                if self.__status.inited():
                    self.profile.update(
                        "LteRrcProfile:" + str(self.__status.id) + "_" + str(self.__status.freq) + ".idle.serv_config",
                        {'priority': field_val['lte-rrc.cellReselectionPriority'],
                         'threshserv_low': str(int(field_val['lte-rrc.threshServingLow']) * 2),
                         's_nonintrasearch': str(float(field_val['lte-rrc.s_NonIntraSearch']) * 2),
                         'q_hyst': field_val['lte-rrc.q_Hyst']})

                self.__config[cur_pair].sib.intra_freq_config = LteRrcSibIntraFreqConfig(
                    int(field_val['lte-rrc.t_ReselectionEUTRA']),
                    int(field_val['lte-rrc.utra_q_RxLevMin']) * 2,
                    int(field_val['lte-rrc.p_Max']),
                    float(field_val['lte-rrc.s_IntraSearch']) * 2)

                # Test profile
                if self.__status.inited():
                    self.profile.update("LteRrcProfile:" + str(self.__status.id) + "_" + str(
                        self.__status.freq) + ".idle.intra_freq_config",
                                        {'tReselection': field_val['lte-rrc.t_ReselectionEUTRA'],
                                         'q_RxLevMin': str(int(field_val['lte-rrc.utra_q_RxLevMin']) * 2),
                                         'p_Max': field_val['lte-rrc.p_Max'],
                                         's_IntraSearch': str(float(field_val['lte-rrc.s_IntraSearch']) * 2)})
                self.broadcast_info('SIB_CONFIG', self.__config[cur_pair].dump_dict())
                self.log_info('SIB_CONFIG: ' + str(self.__config[cur_pair].dump()))
            # inter-frequency (LTE)
            if field.get('name') == "lte-rrc.interFreqCarrierFreqList":
                field_val = {}

                # FIXME: set to the default value based on TS36.331
                field_val['lte-rrc.dl_CarrierFreq'] = 0  # mandatory
                field_val['lte-rrc.t_ReselectionEUTRA'] = 0  # mandatory
                field_val['lte-rrc.utra_q_RxLevMin'] = 0  # mandatory
                field_val['lte-rrc.p_Max'] = 23  # optional, r.f. 36.101
                field_val['lte-rrc.cellReselectionPriority'] = 0  # mandatory
                field_val['lte-rrc.threshX_High'] = 0  # mandatory
                field_val['lte-rrc.threshX_Low'] = 0  # mandatory
                field_val['lte-rrc.q_OffsetFreq'] = 0

                for val in field.iter('field'):
                    field_val[val.get('name')] = val.get('show')

                cur_pair = (self.__status.id, self.__status.freq)
                if cur_pair not in self.__config:
                    self.__config[cur_pair] = LteRrcConfig()
                    self.__config[cur_pair].status = self.__status

                neighbor_freq = int(field_val['lte-rrc.dl_CarrierFreq'])
                self.__config[cur_pair].sib.inter_freq_config[neighbor_freq] = LteRrcSibInterFreqConfig(
                    "LTE",
                    neighbor_freq,
                    int(field_val['lte-rrc.t_ReselectionEUTRA']),
                    int(field_val['lte-rrc.q_RxLevMin']) * 2,
                    int(field_val['lte-rrc.p_Max']),
                    int(field_val['lte-rrc.cellReselectionPriority']),
                    int(field_val['lte-rrc.threshX_High']) * 2,
                    int(field_val['lte-rrc.threshX_Low']) * 2,
                    int(field_val['lte-rrc.q_OffsetFreq']))

                # Test profile
                if self.__status.inited():
                    self.profile.update("LteRrcProfile:" + str(self.__status.id) + "_" + str(
                        self.__status.freq) + ".idle.inter_freq_config:" + str(neighbor_freq),
                                        {'rat': 'LTE',
                                         'freq': str(neighbor_freq),
                                         'tReselection': field_val['lte-rrc.t_ReselectionEUTRA'],
                                         'q_RxLevMin': str(int(field_val['lte-rrc.q_RxLevMin']) * 2),
                                         'p_Max': field_val['lte-rrc.p_Max'],
                                         'priority': field_val['lte-rrc.cellReselectionPriority'],
                                         'threshx_high': str(int(field_val['lte-rrc.threshX_High']) * 2),
                                         'threshx_low': str(int(field_val['lte-rrc.threshX_Low']) * 2),
                                         'q_offset_freq': field_val['lte-rrc.q_OffsetFreq']
                                         })

                # 2nd round: inter-freq cell individual offset
                for val in field.iter('field'):
                    if val.get('name') == "lte-rrc.InterFreqNeighCellInfo_element":
                        field_val2 = {}

                        field_val2['lte-rrc.physCellId'] = None  # mandatory
                        field_val2['lte-rrc.q_OffsetCell'] = None  # mandatory

                        for val2 in field.iter('field'):
                            field_val2[val2.get('name')] = val2.get('show')

                        cell_id = int(field_val2['lte-rrc.physCellId'])
                        offset = int(field_val2['lte-rrc.q_OffsetCell'])
                        offset_pair = (cell_id, neighbor_freq)
                        self.__config[cur_pair].sib.inter_freq_cell_config[offset_pair] = q_offset_range[int(offset)]

                self.broadcast_info('SIB_CONFIG', self.__config[cur_pair].dump_dict())
                self.log_info('SIB_CONFIG: ' + str(self.__config[cur_pair].dump()))

            # inter-RAT (UTRA)
            if field.get('name') == "lte-rrc.CarrierFreqUTRA_FDD_element":
                field_val = {}

                # Default value setting
                # FIXME: set to default based on TS25.331
                field_val['lte-rrc.carrierFreq'] = 0  # mandatory
                field_val['lte-rrc.utra_q_RxLevMin'] = 0  # mandatory
                field_val['lte-rrc.p_MaxUTRA'] = 0  # mandatory
                field_val['lte-rrc.cellReselectionPriority'] = 0  # mandatory
                field_val['lte-rrc.threshX_High'] = 0  # mandatory
                field_val['lte-rrc.threshX_High'] = 0  # mandatory

                for val in field.iter('field'):
                    field_val[val.get('name')] = val.get('show')

                cur_pair = (self.__status.id, self.__status.freq)
                if cur_pair not in self.__config:
                    self.__config[cur_pair] = LteRrcConfig()
                    self.__config[cur_pair].status = self.__status

                neighbor_freq = int(field_val['lte-rrc.carrierFreq'])
                self.__config[cur_pair].sib.inter_freq_config[neighbor_freq] = LteRrcSibInterFreqConfig(
                    "UTRA",
                    neighbor_freq,
                    None,  # For 3G, tReselection is not in this IE
                    int(field_val['lte-rrc.utra_q_RxLevMin']) * 2,
                    int(field_val['lte-rrc.p_MaxUTRA']),
                    int(field_val['lte-rrc.cellReselectionPriority']),
                    int(field_val['lte-rrc.threshX_High']) * 2,
                    int(field_val['lte-rrc.threshX_Low']) * 2,
                    0)  # inter-RAT has no freq-offset

                # Test profile
                if self.__status.inited():
                    self.profile.update("LteRrcProfile:" + str(self.__status.id) + "_" + str(
                        self.__status.freq) + ".idle.inter_freq_config:" + str(neighbor_freq),
                                        {'rat': 'UTRA',
                                         'freq': str(neighbor_freq),
                                         'tReselection': 'null',
                                         'q_RxLevMin': str(int(field_val['lte-rrc.utra_q_RxLevMin']) * 2),
                                         'p_Max': field_val['lte-rrc.p_MaxUTRA'],
                                         'priority': field_val['lte-rrc.cellReselectionPriority'],
                                         'threshx_high': str(int(field_val['lte-rrc.threshX_High']) * 2),
                                         'threshx_low': str(int(field_val['lte-rrc.threshX_Low']) * 2),
                                         'q_offset_freq': '0'
                                         })

                self.broadcast_info('SIB_CONFIG', self.__config[cur_pair].dump_dict())
                
                self.log_info('SIB_CONFIG: ' + str(self.__config[cur_pair].dump()))

            if field.get('name') == "lte-rrc.t_ReselectionUTRA":
                cur_pair = (self.__status.id, self.__status.freq)
                if cur_pair not in self.__config:
                    self.__config[cur_pair] = LteRrcConfig()
                    self.__config[cur_pair].status = self.__status
                    # return
                for config in list(self.__config[cur_pair].sib.inter_freq_config.values()):
                    if config.rat == "UTRA":
                        config.tReselection = float(field.get('show'))

            # TODO: inter-RAT (GERAN): lte-rrc.CarrierFreqsInfoGERAN_element
            if field.get('name') == "lte-rrc.CarrierFreqsInfoGERAN_element":
                field_val = {}

                # Default value setting
                # FIXME: set to default based on TS25.331
                field_val['lte-rrc.startingARFCN'] = 0  # mandatory
                field_val['lte-rrc.utra_q_RxLevMin'] = 0  # mandatory
                field_val['lte-rrc.p_MaxGERAN'] = 0  # mandatory
                field_val['lte-rrc.cellReselectionPriority'] = 0  # mandatory
                field_val['lte-rrc.threshX_High'] = 0  # mandatory
                field_val['lte-rrc.threshX_High'] = 0  # mandatory

                for val in field.iter('field'):
                    field_val[val.get('name')] = val.get('show')

                cur_pair = (self.__status.id, self.__status.freq)
                if cur_pair not in self.__config:
                    self.__config[cur_pair] = LteRrcConfig()
                    self.__config[cur_pair].status = self.__status

                neighbor_freq = int(field_val['lte-rrc.startingARFCN'])
                self.__config[cur_pair].sib.inter_freq_config[neighbor_freq] = LteRrcSibInterFreqConfig(
                    "GERAN",
                    neighbor_freq,
                    None,  # For 3G, tReselection is not in this IE
                    int(field_val['lte-rrc.utra_q_RxLevMin']) * 2,
                    int(field_val['lte-rrc.p_MaxGERAN']),
                    int(field_val['lte-rrc.cellReselectionPriority']),
                    int(field_val['lte-rrc.threshX_High']) * 2,
                    int(field_val['lte-rrc.threshX_Low']) * 2,
                    0)  # inter-RAT has no freq-offset

                # Test profile
                if self.__status.inited():
                    self.profile.update("LteRrcProfile:" + str(self.__status.id) + "_" + str(
                        self.__status.freq) + ".idle.inter_freq_config:" + str(neighbor_freq),
                                        {'rat': 'GERAN',
                                         'freq': str(neighbor_freq),
                                         'tReselection': 'null',
                                         'q_RxLevMin': str(int(field_val['lte-rrc.utra_q_RxLevMin']) * 2),
                                         'p_Max': field_val['lte-rrc.p_MaxGERAN'],
                                         'priority': field_val['lte-rrc.cellReselectionPriority'],
                                         'threshx_high': str(int(field_val['lte-rrc.threshX_High']) * 2),
                                         'threshx_low': str(int(field_val['lte-rrc.threshX_Low']) * 2),
                                         'q_offset_freq': '0'
                                         })
                self.broadcast_info('SIB_CONFIG', self.__config[cur_pair].dump_dict())
                self.log_info('SIB_CONFIG: ' + str(self.__config[cur_pair].dump()))

            # FIXME: t_ReselectionGERAN appears BEFORE config, so this code does not work!
            if field.get('name') == "lte-rrc.t_ReselectionGERAN":
                cur_pair = (self.__status.id, self.__status.freq)
                if cur_pair not in self.__config:
                    self.__config[cur_pair] = LteRrcConfig()
                    self.__config[cur_pair].status = self.__status
                for config in list(self.__config[cur_pair].sib.inter_freq_config.values()):
                    if config.rat == "GERAN":
                        config.tReselection = float(field.get('show'))
                self.broadcast_info('SIB_CONFIG', self.__config[cur_pair].dump_dict())
                self.log_info('SIB_CONFIG: ' + str(self.__config[cur_pair].dump()))

            # intra-frequency cell offset
            if field.get('name') == "lte-rrc.IntraFreqNeighCellInfo_element":
                field_val = {}

                field_val['lte-rrc.physCellId'] = 0  # mandatory
                field_val['lte-rrc.q_OffsetCell'] = 0  # mandatory

                for val in field.iter('field'):
                    field_val[val.get('name')] = val.get('show')

                cur_pair = (self.__status.id, self.__status.freq)
                if cur_pair not in self.__config:
                    self.__config[cur_pair] = LteRrcConfig()
                    self.__config[cur_pair].status = self.__status

                cell_id = int(field_val['lte-rrc.physCellId'])
                offset = int(field_val['lte-rrc.q_OffsetCell'])
                self.__config[cur_pair].sib.intra_freq_cell_config[cell_id] = q_offset_range[int(offset)]
                self.broadcast_info('SIB_CONFIG', self.__config[cur_pair].dump_dict())
                self.log_info('SIB_CONFIG: ' + str(self.__config[cur_pair].dump()))

                # TODO: RRC connection status update

    def __callback_rrc_reconfig(self, msg):

        """
        Extract configurations from RRCReconfiguration Message,
        including the measurement profiles, the MAC/RLC/PDCP configurations, etc.

        :param msg: LTE RRC reconfiguration messages
        """

        # TODO: optimize code to handle objects/config under the same ID
        measobj_id = -1
        report_id = -1

        for field in msg.data.iter('field'):

            if field.get('name') == "lte-rrc.measObjectId":
                measobj_id = int(field.get('show'))

            if field.get('name') == "lte-rrc.reportConfigId":
                report_id = int(field.get('show'))

            # Add a LTE measurement object
            if field.get('name') == "lte-rrc.measObjectEUTRA_element":
                field_val = {}

                field_val['lte-rrc.carrierFreq'] = 0
                field_val['lte-rrc.offsetFreq'] = 0

                for val in field.iter('field'):
                    field_val[val.get('name')] = val.get('show')

                cur_pair = (self.__status.id, self.__status.freq)
                if cur_pair not in self.__config:
                    self.__config[cur_pair] = LteRrcConfig()
                    self.__config[cur_pair].status = self.__status

                freq = int(field_val['lte-rrc.carrierFreq'])
                offsetFreq = int(field_val['lte-rrc.offsetFreq'])
                self.__config[cur_pair].active.measobj[freq] = LteMeasObjectEutra(measobj_id, freq, offsetFreq)

                # 2nd round: handle cell individual offset
                for val in field.iter('field'):
                    if val.get('name') == 'lte-rrc.CellsToAddMod_element':
                        cell_val = {}
                        for item in val.iter('field'):
                            cell_val[item.get('name')] = item.get('show')

                        if 'lte-rrc.physCellId' in cell_val:
                            cell_id = int(cell_val['lte-rrc.physCellId'])
                            if 'lte-rrc.cellIndividualOffset' in cell_val:
                                cell_offset = q_offset_range[int(cell_val['lte-rrc.cellIndividualOffset'])]
                            else:
                                cell_offset = 0
                            self.__config[cur_pair].active.measobj[freq].add_cell(cell_id, cell_offset)

                self.broadcast_info('RRC_RECONFIG', self.__config[cur_pair].dump_dict())
                self.log_info('RRC_RECONFIG: ' + str(self.__config[cur_pair].dump()))

            # Add a NR (5G) measurement object (5G-NSA: in order to add NR cell as secondaryGroup for EN-DC)
            if field.get('name') == "lte-rrc.measObjectNR_r15_element":
                freq = None
                for val in field.iter('field'):
                    if val.get('name') == "lte-rrc.carrierFreq_r15":
                        freq = int(val.get('show'))
                        break
                if freq is not None:
                    cur_pair = (self.__status.id, self.__status.freq)
                    if cur_pair not in self.__config:
                        self.__config[cur_pair] = LteRrcConfig()
                        self.__config[cur_pair].status = self.__status
                    self.__config[cur_pair].active.measobj[freq] = LteMeasObjectNr(measobj_id, freq, None)

            # Add a UTRA (3G) measurement object:
            if field.get('name') == "lte-rrc.measObjectUTRA_element":
                field_val = {}

                field_val['lte-rrc.carrierFreq'] = 0
                field_val['lte-rrc.offsetFreq'] = 0

                for val in field.iter('field'):
                    field_val[val.get('name')] = val.get('show')

                cur_pair = (self.__status.id, self.__status.freq)
                if cur_pair not in self.__config:
                    self.__config[cur_pair] = LteRrcConfig()
                    self.__config[cur_pair].status = self.__status

                freq = int(field_val['lte-rrc.carrierFreq'])
                offsetFreq = int(field_val['lte-rrc.offsetFreq'])
                self.__config[cur_pair].active.measobj[freq] = LteMeasObjectUtra(measobj_id, freq, offsetFreq)

            # Add a LTE report configuration
            if field.get('name') == "lte-rrc.reportConfigEUTRA_element":

                cur_pair = (self.__status.id, self.__status.freq)
                if cur_pair not in self.__config:
                    self.__config[cur_pair] = LteRrcConfig()
                    self.__config[cur_pair].status = self.__status

                hyst = 0
                for val in field.iter('field'):
                    if val.get('name') == 'lte-rrc.hysteresis':
                        hyst = int(val.get('show'))

                report_config = LteReportConfig(report_id, hyst / 2)

                for val in field.iter('field'):

                    if val.get('name') == 'lte-rrc.eventA1_element':
                        for item in val.iter('field'):
                            if item.get('name') == 'lte-rrc.threshold_RSRP':
                                report_config.add_event('a1', int(item.get('show')) - 130)
                                break
                            if item.get('name') == 'lte-rrc.threshold_RSRQ':
                                report_config.add_event('a1', (int(item.get('show')) - 39) / 2)
                                break

                    if val.get('name') == 'lte-rrc.eventA2_element':
                        for item in val.iter('field'):
                            if item.get('name') == 'lte-rrc.threshold_RSRP':
                                report_config.add_event('a2', int(item.get('show')) - 130)
                                break
                            if item.get('name') == 'lte-rrc.threshold_RSRQ':
                                report_config.add_event('a2', (int(item.get('show')) - 39) / 2)
                                break

                    if val.get('name') == 'lte-rrc.eventA3_element':
                        for item in val.iter('field'):
                            if item.get('name') == 'lte-rrc.a3_Offset':
                                report_config.add_event('a3', int(item.get('show')) / 2)
                                break

                    if val.get('name') == 'lte-rrc.eventA4_element':
                        for item in val.iter('field'):
                            if item.get('name') == 'lte-rrc.threshold_RSRP':
                                report_config.add_event('a4', int(item.get('show')) - 130)
                                break
                            if item.get('name') == 'lte-rrc.threshold_RSRQ':
                                report_config.add_event('a4', (int(item.get('show')) - 39) / 2)
                                break

                    if val.get('name') == 'lte-rrc.eventA5_element':
                        threshold1 = None
                        threshold2 = None
                        for item in val.iter('field'):
                            if item.get('name') == 'lte-rrc.a5_Threshold1':
                                for item2 in item.iter('field'):
                                    if item2.get('name') == 'lte-rrc.threshold_RSRP':
                                        threshold1 = int(item2.get('show')) - 130
                                        break
                                    if item2.get('name') == 'lte-rrc.threshold_RSRQ':
                                        threshold1 = (int(item2.get('show')) - 39) / 2
                                        break
                            if item.get('name') == 'lte-rrc.a5_Threshold2':
                                for item2 in item.iter('field'):
                                    if item2.get('name') == 'lte-rrc.threshold_RSRP':
                                        threshold2 = int(item2.get('show')) - 130
                                        break
                                    if item2.get('name') == 'lte-rrc.threshold_RSRQ':
                                        threshold2 = (int(item2.get('show')) - 39) / 2
                                        break
                        report_config.add_event('a5', threshold1, threshold2)

                    if val.get('name') == 'lte-rrc.eventB2_element':

                        threshold1 = None
                        threshold2 = None
                        for item in val.iter('field'):
                            if item.get('name') == 'lte-rrc.b2_Threshold1':
                                for item2 in item.iter('field'):
                                    if item2.get('name') == 'lte-rrc.threshold_RSRP':
                                        threshold1 = int(item2.get('show')) - 130
                                        break
                                    if item2.get('name') == 'lte-rrc.threshold_RSRQ':
                                        threshold1 = (int(item2.get('show')) - 39) / 2
                                        break
                            if item.get('name') == 'lte-rrc.b2_Threshold2':
                                for item2 in item.iter('field'):
                                    if item2.get('name') == 'lte-rrc.threshold_RSRP':
                                        threshold2 = int(item2.get('show')) - 130
                                        break
                                    if item2.get('name') == 'lte-rrc.threshold_RSRQ':
                                        threshold2 = (int(item2.get('show')) - 39) / 2
                                        break
                                    if item2.get('name') == 'lte-rrc.utra_RSCP':
                                        threshold2 = int(item2.get('show')) - 115
                                        break
                        report_config.add_event('b2', threshold1, threshold2)

                self.__config[cur_pair].active.report_list[report_id] = report_config

            # Add a 2G/3G report configuration
            if field.get('name') == "lte-rrc.reportConfigInterRAT_element":

                cur_pair = (self.__status.id, self.__status.freq)
                if cur_pair not in self.__config:
                    self.__config[cur_pair] = LteRrcConfig()
                    self.__config[cur_pair].status = self.__status

                hyst = 0
                for val in field.iter('field'):
                    if val.get('name') == 'lte-rrc.hysteresis':
                        hyst = int(val.get('show'))

                report_config = LteReportConfig(report_id, hyst / 2)

                for val in field.iter('field'):

                    if val.get('name') == 'lte-rrc.eventB1_element':
                        for item in val.iter('field'):
                            if item.get('name') == 'lte-rrc.threshold_RSRP':
                                report_config.add_event('b1', int(item.get('show')) - 130)
                                break
                            if item.get('name') == 'lte-rrc.threshold_RSRQ':
                                report_config.add_event('b1', (int(item.get('show')) - 39) / 2)
                                break
                            if item.get('name') == 'lte-rrc.threshold_RSCP':
                                report_config.add_event('b1', int(item.get('show')) - 115)
                                break

                    if val.get('name') == 'lte-rrc.eventB2_element':

                        threshold1 = None
                        threshold2 = None
                        for item in val.iter('field'):
                            if item.get('name') == 'lte-rrc.b2_Threshold1':
                                for item2 in item.iter('field'):
                                    if item2.get('name') == 'lte-rrc.threshold_RSRP':
                                        threshold1 = int(item.get('show')) - 130
                                        break
                                    if item2.get('name') == 'lte-rrc.threshold_RSRQ':
                                        threshold1 = (int(item.get('show')) - 39) / 2
                                        break
                            if item.get('name') == 'lte-rrc.b2_Threshold2':
                                for item2 in item.iter('field'):
                                    if item2.get('name') == 'lte-rrc.threshold_RSRP':
                                        threshold2 = int(item.get('show')) - 130
                                        break
                                    if item2.get('name') == 'lte-rrc.threshold_RSRQ':
                                        threshold2 = (int(item.get('show')) - 39) / 2
                                        break
                                    if item2.get('name') == 'lte-rrc.utra_RSCP':
                                        threshold2 = int(item.get('show')) - 115
                                        break
                        report_config.add_event('b2', threshold1, threshold2)

                    if val.get('name') == "lte-rrc.eventB1_NR_r15_element":
                        threshold = None
                        quantity = None
                        for item in val.iter('field'):
                            if item.get('name') == "lte-rrc.b1_ThresholdNR_r15":
                                for item2 in item.iter('field'):
                                    if item2.get('name') == "lte-rrc.nr_RSRP_r15":
                                        threshold = int(item2.get('show')) - 156
                                        quantity = 'RSRP'
                                        break
                                    if item2.get('name') == "lte-rrc.nr_RSRQ_r15":
                                        threshold = int(item2.get('show')) / 2.0 - 43
                                        quantity = 'RSRQ'
                                        break
                                    if item2.get('name') == "lte-rrc.nr_SINR_r15":
                                        threshold = int(item2.get('show')) / 2.0 - 23
                                        quantity = 'SINR'
                                        break
                        report_config.add_event('b1', threshold, None)

                self.__config[cur_pair].active.report_list[report_id] = report_config

            # Add a LTE measurement report config
            if field.get('name') == "lte-rrc.MeasIdToAddMod_element":
                field_val = {}
                for val in field.iter('field'):
                    field_val[val.get('name')] = val.get('show')

                cur_pair = (self.__status.id, self.__status.freq)
                if cur_pair not in self.__config:
                    self.__config[cur_pair] = LteRrcConfig()
                    self.__config[cur_pair].status = self.__status

                meas_id = int(field_val['lte-rrc.measId'])
                obj_id = int(field_val['lte-rrc.measObjectId'])
                config_id = int(field_val['lte-rrc.reportConfigId'])
                self.__config[cur_pair].active.measid_list[meas_id] = (obj_id, config_id)

            # Measurement for NR objects
            if field.get('name') == "lte-rrc.measResults_element":
                meas_id = None
                NR_cells = []
                for val in field.iter('field'):
                    if val.get('name') == "lte-rrc.measId":
                        meas_id = int(val.get('show'))
                    if val.get('name') == "lte-rrc.MeasResultCellNR_r15_element":
                        pci = None
                        rsrp = None
                        for item in val.iter('field'):
                            if item.get('name') == "lte-rrc.pci_r15":
                                pci = int(item.get('show'))
                            if item.get('name') == "lte-rrc.measResultCell_r15_element":
                                for sub in item.iter('field'):
                                    if sub.get('name') == "lte-rrc.rsrpResult_r15":
                                        rsrp = int(sub.get('show')) - 156
                                    break
                                break
                        if pci:
                            NR_cells.append({"lte-rrc.pci_r15":pci, "lte-rrc.rsrpResult_r15":rsrp})
                
                if NR_cells:   
                    cur_pair = (self.__status.id, self.__status.freq)
                    config_str = 'None'
                    obj_str = 'None'
                    if cur_pair in self.__config and meas_id in self.__config[cur_pair].active.measid_list:
                        obj_id,config_id = self.__config[cur_pair].active.measid_list[meas_id]
                    
                        if config_id in self.__config[cur_pair].active.report_list:
                            config_str = self.__config[cur_pair].active.report_list[config_id].dump()
                    
                        for key,obj in self.__config[cur_pair].active.measobj.items():
                            if obj.obj_id == obj_id:
                                obj_str = obj.dump()
                                break
                    self.log_info("NR_RRC_REPORT " + str(msg.timestamp) + " " +
                        "meas_object: " + obj_str + " " +
                        "config: " + config_str + " " +
                        "NR cells: " + str(NR_cells))               

    def __callback_rrc_conn(self, msg):
        """
        Update RRC connectivity status

        :param msg: the RRC message
        """
        for field in msg.data.iter('field'):
            if field.get('name') == "lte-rrc.rrcConnectionSetupComplete_element":
                self.__status.conn = True
                # self.log_info(self.__status.dump())
                # self.log_info("FSM test: "+self.get_protocol_state())

                drx_state = {}
                drx_state['Conn state'] = "CONNECTED"
                drx_state['DRX state'] = "CRX"
                drx_state['Timestamp'] = str(msg.timestamp)
                self.broadcast_info('DRX', drx_state)

            if field.get('name') == "lte-rrc.rrcConnectionRelease_element":
                self.__status.conn = False
                # self.log_info(self.__status.dump())
                # self.log_info("FSM test: "+self.get_protocol_state())

                drx_state = {}
                drx_state['Conn state'] = "IDLE"
                drx_state['DRX state'] = "IDLE"
                drx_state['Timestamp'] = str(msg.timestamp)
                self.broadcast_info('DRX', drx_state)

            if field.get('name') == "lte-rrc.nr_Config_r15":
                setup = None
                for var in field.iter('field'):
                    if setup is None and var.get('name') == "lte-rrc.setup_element":
                        setup = True
                    if setup is None and var.get('name') == "lte-rrc.release_element":
                        setup = False
                        self.log_info("RELEASE_NR_CELL " + str(msg.timestamp))
                    if var.get('name') == "nr-rrc.spCellConfigCommon_element":
                        pci = None
                        freq = None
                        for item in var.iter('field'):
                            if item.get('name') == "nr-rrc.physCellId":
                                pci = int(item.get('show'))
                            if item.get('name') == "nr-rrc.absoluteFrequencySSB":
                                freq = int(item.get('show'))
                                break
                        if pci and freq:
                            self.log_info('UPDATA_NR_CELL ' + str(msg.timestamp) + ' ' + str((freq,pci)))

            if field.get('name') == "lte-rrc.mobilityControlInfo_element":
                pci = None
                freq = None
                for val in field.iter('field'):
                    if val.get('name') == "lte-rrc.targetPhysCellId":
                        pci = int(val.get('show'))
                    if val.get('name') == "lte-rrc.dl_CarrierFreq":
                        freq = int(val.get('show'))
                        break
                if pci and freq:
                    self.log_info('HANDOVER ' + str(msg.timestamp) + ' from ' + str((self.__status.freq, self.__status.id)) + ' to ' + str((freq,pci)))
                    self.__update_conn(msg.timestamp,freq,pci)

    def __update_conn(self, timestamp, freq, pci):
        status_updated = False
        if not self.__status.inited():
            status_updated = True
            self.__status.freq = freq
            self.__status.id = pci
        elif self.__status.freq != freq or self.__status.id != pci:
            status_updated = True
            curr_conn = self.__status.conn
            self.__status = LteRrcStatus()
            self.__status.conn = curr_conn
            self.__status.freq = freq
            self.__status.id = pci
            # self.__status.tac = None

        if status_updated:
            self.log_info(self.__status.dump())
            self.broadcast_info('LTE_RRC_STATUS', self.__status.dump_dict())

    def set_source(self, source):
        """
        Set the trace source. Enable the LTE RRC messages.

        :param source: the trace source.
        :type source: trace collector
        """
        Analyzer.set_source(self, source)
        # enable LTE RRC log
        source.enable_log("LTE_RRC_OTA_Packet")
        source.enable_log("LTE_RRC_Serv_Cell_Info")
        source.enable_log("LTE_RRC_CDRX_Events_Info")

    def get_cell_list(self):
        """
        Get a complete list of cell IDs.

        :returns: a list of cells the device has associated with
        """
        # FIXME: currently only return *all* cells in the LteRrcConfig
        return list(self.__config.keys())

    def get_cell_config(self, cell):
        """
        Return a cell's active/idle-state configuration.

        :param cell:  a cell identifier
        :type cell: a (cell_id,freq) pair
        :returns: this cell's active/idle-state configurations
        :rtype: LteRrcConfig
        """
        if cell in self.__config:
            return self.__config[cell]
        else:
            return None

    def get_cur_cellid(self):
        """
        Get current cell's ID

        :return: current cell's ID
        """

        return self.__status.id if self.__status else None

    def get_cur_freq(self):
        """
        Get current cell's EARFCN
        """

        return self.__status.freq if self.__status else None

    def get_cur_cell(self):
        """
        Get current cell's status

        :returns: current cell's status
        :rtype: LteRrcStatus
        """
        return self.__status

    def get_cur_cell_config(self):
        """
        Get current cell's configuration

        :returns: current cell's status
        :rtype: LteRrcConfig
        """
        cur_pair = (self.__status.id, self.__status.freq)
        if cur_pair in self.__config:
            return self.__config[cur_pair]
        else:
            return None

    def get_mobility_history(self):
        """
        Get the history of cells the device associates with

        :returns: the cells the device has traversed
        :rtype: a dictionary of timestamp -> LteRrcStatus
        """
        return self.__history