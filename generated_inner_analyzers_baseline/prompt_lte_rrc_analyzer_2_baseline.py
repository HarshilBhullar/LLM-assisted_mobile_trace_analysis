
from mobileinsight.analyzer.analyzer import ProtocolAnalyzer

class LteRrcAnalyzerModified(ProtocolAnalyzer):
    def __init__(self):
        super(LteRrcAnalyzerModified, self).__init__()
        self.__state_machine = self.__initialize_state_machine()
        self.__cell_status = {}
        self.__mobility_history = []

        # Configure packet filters for RRC messages
        self.add_source_callback(self.__callback_rrc_conn, "LTE_RRC_OTA_Packet")
        self.add_source_callback(self.__callback_sib_config, "LTE_RRC_OTA_Packet")
        self.add_source_callback(self.__callback_rrc_reconfig, "LTE_RRC_OTA_Packet")
        self.add_source_callback(self.__callback_drx, "LTE_RRC_OTA_Packet")

    def __initialize_state_machine(self):
        # Initialize state machine with defined RRC states
        state_machine = {
            'IDLE': {'CRX': self.__handle_idle_to_crx},
            'CRX': {'IDLE': self.__handle_crx_to_idle},
            # Add additional states and transitions as needed
        }
        return state_machine

    def __handle_idle_to_crx(self, message):
        # Handle transition from IDLE to CRX
        self.__cell_status['state'] = 'CRX'
        self.__update_mobility_history('CRX', message)

    def __handle_crx_to_idle(self, message):
        # Handle transition from CRX to IDLE
        self.__cell_status['state'] = 'IDLE'
        self.__update_mobility_history('IDLE', message)

    def __callback_rrc_conn(self, msg):
        # Update connectivity status based on connection setup and release messages
        if 'ConnectionSetup' in msg:
            self.__state_machine['IDLE']['CRX'](msg)
        elif 'ConnectionRelease' in msg:
            self.__state_machine['CRX']['IDLE'](msg)

    def __callback_sib_config(self, msg):
        # Extract configurations from SIBs
        if 'SIB' in msg:
            self.__cell_status['sib'] = msg['SIB']

    def __callback_rrc_reconfig(self, msg):
        # Analyze RRCReconfiguration messages
        if 'RRCReconfiguration' in msg:
            self.__cell_status['reconfig'] = msg['RRCReconfiguration']

    def __callback_drx(self, msg):
        # Broadcast DRX state changes
        if 'DRX' in msg:
            self.__cell_status['drx'] = msg['DRX']

    def __update_mobility_history(self, state, message):
        # Update mobility history
        self.__mobility_history.append({'state': state, 'message': message})

    def get_profile_hierarchy(self):
        # Return a profile hierarchy for LTE RRC configurations
        return {
            'status': self.__cell_status,
            'mobility_history': self.__mobility_history
        }

    def get_current_cell_id(self):
        # Retrieve the current cell ID
        return self.__cell_status.get('cell_id', None)

    def get_current_frequency(self):
        # Retrieve the current frequency
        return self.__cell_status.get('frequency', None)

    def get_current_status(self):
        # Retrieve the current status
        return self.__cell_status.get('state', 'UNKNOWN')
