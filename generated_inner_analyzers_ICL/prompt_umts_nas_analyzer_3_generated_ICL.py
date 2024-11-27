
#!/usr/bin/python
# Filename: umts_nas_analyzer_modified.py
"""
A modified UMTS NAS analyzer to extract and analyze NAS events with modified settings.

Author: Adapted by Assistant
"""

from mobile_insight.analyzer.analyzer import *
from mobile_insight.analyzer.protocol_analyzer import *

__all__ = ["UmtsNasAnalyzerModified"]

class UmtsNasAnalyzerModified(ProtocolAnalyzer):
    """
    A modified protocol analyzer for UMTS NAS.
    """

    def __init__(self):
        print("Init Modified UMTS NAS Analyzer")
        ProtocolAnalyzer.__init__(self)
        
        # Initialize state machines
        self.mm_state_machine = self.create_mm_state_machine()
        self.gmm_state_machine = self.create_gmm_state_machine()
        self.cm_state_machine = self.create_cm_state_machine()

        # Setup packet filters
        self.add_source_callback(self.__nas_filter)

        # Initialize internal states
        self.__mm_status = MmStatus()
        self.__gmm_status = GmmStatus()
        self.__cm_status = CmStatus()

    def create_profile_hierarchy(self):
        """
        Return a UMTS NAS ProfileHierarchy (configurations)

        :returns: ProfileHierarchy for UMTS NAS
        """
        profile_hierarchy = ProfileHierarchy('UmtsNasProfile')
        root = profile_hierarchy.get_root()
        root.add('mm_status', False)
        root.add('gmm_status', False)
        root.add('cm_status', False)

        return profile_hierarchy

    def create_mm_state_machine(self):
        """
        Declare a MM state machine

        returns: a StateMachine
        """
        def idle_to_connected(msg):
            if msg.type_id == "UMTS_NAS_MM_State":
                return msg.data['state'] == "CONNECTED"

        def connected_to_idle(msg):
            if msg.type_id == "UMTS_NAS_MM_State":
                return msg.data['state'] == "IDLE"

        state_machine = {
            'IDLE': {'CONNECTED': idle_to_connected},
            'CONNECTED': {'IDLE': connected_to_idle}
        }

        return StateMachine(state_machine, self.init_mm_state)

    def create_gmm_state_machine(self):
        """
        Declare a GMM state machine

        returns: a StateMachine
        """
        def deregistered_to_registered(msg):
            if msg.type_id == "UMTS_NAS_GMM_State":
                return msg.data['state'] == "REGISTERED"

        def registered_to_deregistered(msg):
            if msg.type_id == "UMTS_NAS_GMM_State":
                return msg.data['state'] == "DEREGISTERED"

        state_machine = {
            'DEREGISTERED': {'REGISTERED': deregistered_to_registered},
            'REGISTERED': {'DEREGISTERED': registered_to_deregistered}
        }

        return StateMachine(state_machine, self.init_gmm_state)

    def create_cm_state_machine(self):
        """
        Declare a CM state machine

        returns: a StateMachine
        """
        def inactive_to_active(msg):
            if msg.type_id == "UMTS_NAS_MM_REG_State":
                return msg.data['state'] == "ACTIVE"

        def active_to_inactive(msg):
            if msg.type_id == "UMTS_NAS_MM_REG_State":
                return msg.data['state'] == "INACTIVE"

        state_machine = {
            'INACTIVE': {'ACTIVE': inactive_to_active},
            'ACTIVE': {'INACTIVE': active_to_inactive}
        }

        return StateMachine(state_machine, self.init_cm_state)

    def init_mm_state(self, msg):
        if msg.type_id == "UMTS_NAS_MM_State":
            return msg.data['state']
        return None

    def init_gmm_state(self, msg):
        if msg.type_id == "UMTS_NAS_GMM_State":
            return msg.data['state']
        return None

    def init_cm_state(self, msg):
        if msg.type_id == "UMTS_NAS_MM_REG_State":
            return msg.data['state']
        return None

    def __nas_filter(self, msg):
        """
        Filter all UMTS NAS packets, and call functions to process them

        :param msg: the event (message) from the trace collector.
        """
        log_item = msg.data.decode()

        if msg.type_id == "UMTS_NAS_OTA_Packet":
            self.__callback_nas(msg)

        elif msg.type_id == "UMTS_NAS_MM_State":
            self.__callback_mm_state(msg)

        elif msg.type_id == "UMTS_NAS_MM_REG_State":
            self.__callback_mm_reg_state(msg)

        elif msg.type_id == "UMTS_NAS_GMM_State":
            self.__callback_gmm_state(msg)

    def __callback_mm_state(self, msg):
        """
        Process and update MM state.

        :param msg: MM state message
        """
        log_item = msg.data.decode()
        self.__mm_status.update_state(log_item['state'])
        broadcast_info = self.__mm_status.dump_dict()
        broadcast_info['additional_info'] = "Modified Analyzer"
        self.broadcast_info('UMTS_MM_STATE', broadcast_info)

    def __callback_mm_reg_state(self, msg):
        """
        Process and update MM REG state.

        :param msg: MM REG state message
        """
        log_item = msg.data.decode()
        self.__cm_status.update_state(log_item['state'])
        broadcast_info = self.__cm_status.dump_dict()
        broadcast_info['additional_info'] = "Modified Analyzer"
        self.broadcast_info('UMTS_MM_REG_STATE', broadcast_info)

    def __callback_gmm_state(self, msg):
        """
        Process and update GMM state.

        :param msg: GMM state message
        """
        log_item = msg.data.decode()
        self.__gmm_status.update_state(log_item['state'])
        broadcast_info = self.__gmm_status.dump_dict()
        broadcast_info['additional_info'] = "Modified Analyzer"
        self.broadcast_info('UMTS_GMM_STATE', broadcast_info)

    def __callback_nas(self, msg):
        """
        Process NAS OTA packets.

        :param msg: NAS OTA Packet
        """
        log_item = msg.data.decode()
        self.broadcast_info('UMTS_NAS_OTA', {'data': log_item, 'additional_info': "Modified Analyzer"})

    def set_source(self, source):
        """
        Set the trace source and enable UMTS NAS messages.

        :param source: the trace source.
        """
        Analyzer.set_source(self, source)
        # Enable UMTS NAS logs
        source.enable_log("UMTS_NAS_OTA_Packet")
        source.enable_log("UMTS_NAS_GMM_State")
        source.enable_log("UMTS_NAS_MM_State")
        source.enable_log("UMTS_NAS_MM_REG_State")
