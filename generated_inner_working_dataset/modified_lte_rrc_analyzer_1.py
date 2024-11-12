
#!/usr/bin/python
# Filename: lte_rrc_analyzer_modified.py
"""
A modified LTE RRC analyzer for additional metrics.
Author: Yuanjie Li, Zhehui Zhang
"""

import xml.etree.ElementTree as ET
from .analyzer import *
from .state_machine import *
from .protocol_analyzer import *
import timeit
import time

from .profile import Profile, ProfileHierarchy

__all__ = ["LteRrcAnalyzerModified"]

# Q-offset range mapping (6.3.4, TS36.331)
q_offset_range = {
    0: -24, 1: -22, 2: -20, 3: -18, 4: -16, 5: -14,
    6: -12, 7: -10, 8: -8, 9: -6, 10: -5, 11: -4,
    12: -3, 13: -2, 14: -1, 15: 0, 16: 1, 17: 2,
    18: 3, 19: 4, 20: 5, 21: 6, 22: 8, 23: 10, 24: 12,
    25: 14, 26: 16, 27: 18, 28: 20, 29: 22, 30: 24
}


class LteRrcAnalyzerModified(ProtocolAnalyzer):
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

    def __rrc_filter(self, msg):
        """
        Filter all LTE RRC packets, and call functions to process it

        :param msg: the event (message) from the trace collector.
        """
        log_item = msg.data.decode()
        log_item_dict = dict(log_item)

        self.send_to_coordinator(Event(msg.timestamp, msg.type_id, str(log_item)))

        # Callbacks triggering
        if msg.type_id == "LTE_RRC_OTA_Packet":

            if 'Msg' not in log_item_dict:
                return

            # Convert msg to xml format
            log_xml = ET.XML(log_item_dict['Msg'])
            xml_msg = Event(log_item_dict['timestamp'], msg.type_id, log_xml)

            if self.state_machine.update_state(xml_msg):
                event = Event(msg.timestamp, 'rrc state', str(self.state_machine.get_current_state()))
                self.send_to_coordinator(event)

            self.__callback_rrc_conn(xml_msg)
            self.__callback_sib_config(xml_msg)
            self.__callback_rrc_reconfig(xml_msg)

            self.send(xml_msg)  # deliver LTE RRC signaling messages (decoded)

        elif msg.type_id == "LTE_RRC_Serv_Cell_Info":
            raw_msg = Event(msg.timestamp, msg.type_id, log_item_dict)
            self.__callback_serv_cell(raw_msg)

        elif msg.type_id == "LTE_RRC_CDRX_Events_Info":
            for item in log_item_dict['Records']:
                raw_msg = Event(' '.join(map(str, [log_item_dict['timestamp'], item['SFN'], item['Sub-FN']])),
                                msg.type_id, item)
                if self.state_machine.update_state(raw_msg):
                    event = Event(msg.timestamp, 'rrc state', str(self.state_machine.get_current_state()))
                    self.send_to_coordinator(event)
            self.__callback_drx(log_item_dict)

    def __callback_sib_config(self, msg):
        """
        A callback to extract configurations from System Information Blocks (SIBs),
        including the radio assessment thresholds, the preference settings, etc.

        :param msg: RRC SIB messages
        """
        for field in msg.data.iter('field'):

            if field.get('name') == 'lte-rrc.measResultPCell_element':
                meas_report = {}
                meas_report['timestamp'] = str(msg.timestamp)
                for val in field.iter('field'):
                    if val.get('name') == 'lte-rrc.rsrpResult':
                        meas_report['rsrp'] = int(val.get('show'))
                        meas_report['rssi'] = meas_report['rsrp'] - 141  # map rsrp to rssi
                    elif val.get('name') == 'lte-rrc.rsrqResult':
                        meas_report['rsrq'] = int(val.get('show'))
                meas_report['rsrp_adjusted'] = meas_report['rsrp'] * 1.1  # Applying a small adjustment
                self.broadcast_info('MEAS_PCELL', meas_report)
                self.log_info('MEAS_PCELL: ' + str(meas_report))
                self.send_to_coordinator(Event(msg.timestamp, 'rsrp', meas_report['rsrp']))
                self.send_to_coordinator(Event(msg.timestamp, 'rsrq', meas_report['rsrq']))
                self.send_to_coordinator(Event(msg.timestamp, 'rsrp_adjusted', meas_report['rsrp_adjusted']))

            if field.get('name') == "lte-rrc.sib3_element":

                field_val = {}

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

                if self.__status.inited():
                    self.profile.update("LteRrcProfile:" + str(self.__status.id) + "_" + str(
                        self.__status.freq) + ".idle.intra_freq_config",
                                        {'tReselection': field_val['lte-rrc.t_ReselectionEUTRA'],
                                         'q_RxLevMin': str(int(field_val['lte-rrc.utra_q_RxLevMin']) * 2),
                                         'p_Max': field_val['lte-rrc.p_Max'],
                                         's_IntraSearch': str(float(field_val['lte-rrc.s_IntraSearch']) * 2)})
                self.broadcast_info('SIB_CONFIG', self.__config[cur_pair].dump_dict())
                self.log_info('SIB_CONFIG: ' + str(self.__config[cur_pair].dump()))

            if field.get('name') == "lte-rrc.interFreqCarrierFreqList":
                field_val = {}

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

    def __callback_rrc_reconfig(self, msg):
        """
        Extract configurations from RRCReconfiguration Message,
        including the measurement profiles, the MAC/RLC/PDCP configurations, etc.

        :param msg: LTE RRC reconfiguration messages
        """
        measobj_id = -1
        report_id = -1

        for field in msg.data.iter('field'):

            if field.get('name') == "lte-rrc.measObjectId":
                measobj_id = int(field.get('show'))

            if field.get('name') == "lte-rrc.reportConfigId":
                report_id = int(field.get('show'))

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

    def set_source(self, source):
        """
        Set the trace source. Enable the LTE RRC messages.

        :param source: the trace source.
        :type source: trace collector
        """
        Analyzer.set_source(self, source)
        source.enable_log("LTE_RRC_OTA_Packet")
        source.enable_log("LTE_RRC_Serv_Cell_Info")
        source.enable_log("LTE_RRC_CDRX_Events_Info")
