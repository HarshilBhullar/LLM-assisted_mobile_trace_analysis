
from mobile_insight.analyzer import ProtocolAnalyzer

class ModifiedWcdmaRrcAnalyzer(ProtocolAnalyzer):
    def __init__(self):
        super().__init__()
        self._state_machine = self.create_state_machine()
        self._configurations = {}
        self._cell_history = []

    def create_state_machine(self):
        state_machine = {
            'IDLE': ['CELL_FACH', 'CELL_PCH'],
            'CELL_FACH': ['CELL_DCH', 'URA_PCH'],
            'CELL_DCH': ['CELL_FACH', 'URA_PCH'],
            'URA_PCH': ['CELL_FACH', 'IDLE'],
            'CELL_PCH': ['CELL_FACH', 'IDLE'],
        }
        return state_machine

    def __rrc_filter(self, msg):
        if "WCDMA_RRC" in msg.type_name:
            return True
        return False

    def __callback_rrc_state(self, msg):
        # Logic to handle RRC state changes
        state_info = msg.get('state')
        if state_info:
            current_state = self._state_machine.get(state_info['current_state'], [])
            # Update internal state, log or process as needed
            print(f"RRC State: {state_info}")

    def __callback_serv_cell(self, msg):
        # Logic to process serving cell information
        cell_info = msg.get('serving_cell')
        if cell_info:
            self._cell_history.append(cell_info)
            print(f"Serving Cell Info: {cell_info}")

    def __callback_sib_config(self, msg):
        # Logic to extract and process SIB configurations
        sib_info = msg.get('sib_config')
        if sib_info:
            self._configurations.update(sib_info)
            print(f"SIB Configurations: {sib_info}")

    def set_source(self, source):
        super().set_source(source)
        self.source.register_callback(self.__rrc_filter, self.__callback_rrc_state)
        self.source.register_callback(self.__rrc_filter, self.__callback_serv_cell)
        self.source.register_callback(self.__rrc_filter, self.__callback_sib_config)

    def create_profile_hierarchy(self):
        profiles = {
            'idle': {'states': ['IDLE', 'CELL_PCH', 'URA_PCH'], 'metadata': {}},
            'active': {'states': ['CELL_FACH', 'CELL_DCH'], 'metadata': {}},
        }
        return profiles

    def get_current_configuration(self):
        return self._configurations

    def get_cell_history(self):
        return self._cell_history
