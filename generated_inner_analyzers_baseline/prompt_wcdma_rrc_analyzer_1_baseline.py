
from mobile_insight.analyzer import ProtocolAnalyzer
import xml.etree.ElementTree as ET

class ModifiedWcdmaRrcAnalyzer(ProtocolAnalyzer):
    def __init__(self):
        super(ModifiedWcdmaRrcAnalyzer, self).__init__()
        self.enable_log("WCDMA_RRC_OTA_Packet")
        self.enable_log("WCDMA_RRC_Serv_Cell_Info")
        self.enable_log("WCDMA_RRC_States")

        self.current_cell_status = None
        self.cell_history = []
        self.configurations = {}

        self.add_callback(self.__rrc_state_callback)
        self.add_callback(self.__serv_cell_info_callback)
        self.add_callback(self.__ota_packet_callback)

    def __rrc_state_callback(self, msg):
        if msg.type_id == "WCDMA_RRC_States":
            state_info = self.__parse_xml(msg.data.decode('utf-8'))
            self.__update_rrc_state(state_info)

    def __serv_cell_info_callback(self, msg):
        if msg.type_id == "WCDMA_RRC_Serv_Cell_Info":
            serv_cell_info = self.__parse_xml(msg.data.decode('utf-8'))
            self.__update_serv_cell_info(serv_cell_info)

    def __ota_packet_callback(self, msg):
        if msg.type_id == "WCDMA_RRC_OTA_Packet":
            ota_packet = self.__parse_xml(msg.data.decode('utf-8'))
            self.__process_ota_packet(ota_packet)

    def __parse_xml(self, xml_data):
        try:
            root = ET.fromstring(xml_data)
            return root
        except ET.ParseError as e:
            print(f"Failed to parse XML: {e}")
            return None

    def __update_rrc_state(self, state_info):
        if state_info is not None:
            current_state = state_info.find("Current_State").text
            if current_state != self.current_cell_status:
                self.current_cell_status = current_state
                self.cell_history.append(current_state)
                self.__on_rrc_state_change(current_state)

    def __update_serv_cell_info(self, serv_cell_info):
        if serv_cell_info is not None:
            cell_id = serv_cell_info.find("Cell_ID").text
            if cell_id not in self.configurations:
                self.configurations[cell_id] = {}
            self.configurations[cell_id]['info'] = serv_cell_info

    def __process_ota_packet(self, ota_packet):
        if ota_packet is not None:
            message_type = ota_packet.find("Message_Type").text
            if message_type == "System_Information_Block":
                self.__process_sib(ota_packet)

    def __process_sib(self, sib_packet):
        sib_config = sib_packet.find("Configuration")
        if sib_config is not None:
            cell_id = sib_packet.find("Cell_ID").text
            if cell_id in self.configurations:
                self.configurations[cell_id]['SIB'] = sib_config

    def __on_rrc_state_change(self, new_state):
        print(f"RRC state changed to: {new_state}")

    def get_associated_cell_ids(self):
        return list(self.configurations.keys())

    def get_current_cell_status(self):
        return self.current_cell_status

    def get_configurations(self):
        return self.configurations
