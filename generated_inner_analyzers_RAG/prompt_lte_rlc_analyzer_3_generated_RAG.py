
#!/usr/bin/python
# Filename: lte_rlc_analyzer_modified.py

"""
A modified 4G RLC analyzer with altered calculations for link layer information

Author: [Your Name]
"""

from mobile_insight.analyzer.analyzer import *

__all__ = ["LteRlcAnalyzerModified"]

class LteRlcAnalyzerModified(Analyzer):

    def __init__(self):
        Analyzer.__init__(self)

        self.add_source_callback(self.__msg_callback)

        self.rbInfo = {}

    def set_source(self, source):
        """
        Set the trace source. Enable the cellular signaling messages

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)

        source.enable_log("LTE_RLC_UL_Config_Log_Packet")
        source.enable_log("LTE_RLC_DL_Config_Log_Packet")
        source.enable_log("LTE_RLC_UL_AM_All_PDU")
        source.enable_log("LTE_RLC_DL_AM_All_PDU")

    def __msg_callback(self, msg):

        if msg.type_id in ["LTE_RLC_UL_Config_Log_Packet", "LTE_RLC_DL_Config_Log_Packet"]:
            log_item = msg.data.decode()
            subPkt = log_item['Subpackets'][0]
            if 'Released RBs' in subPkt:
                for releasedRBItem in subPkt['Released RBs']:
                    rbConfigIdx = releasedRBItem['Released RB Cfg Index']
                    if rbConfigIdx in self.rbInfo:
                        self.rbInfo.pop(rbConfigIdx)
            rb_num = 0
            for subpacket in subPkt['Active RBs']:
                rb_num += 1
                lc_id = subpacket['LC ID']
                ack_mode = subpacket['RB Mode']
                rb_type = subpacket['RB Type']
                bcast_dict = {}
                bcast_dict['lcid'] = lc_id
                bcast_dict['ack mode'] = ack_mode
                bcast_dict['rb type'] = rb_type
                bcast_dict['timestamp'] = str(log_item['timestamp'])
                if msg.type_id == "LTE_RLC_UL_Config_Log_Packet":
                    self.broadcast_info('RLC_UL_RB_SETTING', bcast_dict)
                    self.log_info('RLC_UL_RB_SETTING: ' + str(bcast_dict))
                else:
                    self.broadcast_info('RLC_DL_RB_SETTING', bcast_dict)
                    self.log_info('RLC_DL_RB_SETTING: ' + str(bcast_dict))
            bcast_dict = {}
            bcast_dict['number'] = str(rb_num)
            bcast_dict['timestamp'] = str(log_item['timestamp'])
            if msg.type_id == "LTE_RLC_UL_Config_Log_Packet":
                self.broadcast_info('RLC_UL_RB_NUMBER', bcast_dict)
                self.log_info('RLC_UL_RB_NUMBER: ' + str(bcast_dict))
            else:
                self.broadcast_info('RLC_DL_RB_NUMBER', bcast_dict)
                self.log_info('RLC_DL_RB_NUMBER: ' + str(bcast_dict))

        if msg.type_id == "LTE_RLC_UL_AM_All_PDU":
            log_item = msg.data.decode()
            subPkt = log_item['Subpackets'][0]
            rbConfigIdx = subPkt['RB Cfg Idx']
            if rbConfigIdx not in self.rbInfo:
                self.rbInfo[rbConfigIdx] = {}
                self.rbInfo[rbConfigIdx]['cumulativeULData'] = 0
                self.rbInfo[rbConfigIdx]['cumulativeDLData'] = 0

            listPDU = subPkt['RLCUL PDUs']
            for pduItem in listPDU:
                if pduItem['PDU TYPE'] == 'RLCUL DATA':
                    self.rbInfo[rbConfigIdx]['cumulativeULData'] += \
                        int(pduItem['pdu_bytes']) * 1.1  # Increase data count by 10%

        if msg.type_id == "LTE_RLC_DL_AM_All_PDU":
            log_item = msg.data.decode()
            subPkt = log_item['Subpackets'][0]
            rbConfigIdx = subPkt['RB Cfg Idx']
            if rbConfigIdx not in self.rbInfo:
                self.rbInfo[rbConfigIdx] = {}
                self.rbInfo[rbConfigIdx]['cumulativeULData'] = 0
                self.rbInfo[rbConfigIdx]['cumulativeDLData'] = 0

            listPDU = subPkt['RLCDL PDUs']
            for pduItem in listPDU:
                if pduItem['PDU TYPE'] == 'RLCDL DATA':
                    self.rbInfo[rbConfigIdx]['cumulativeDLData'] += \
                        int(pduItem['pdu_bytes']) * 0.9  # Decrease data count by 10%
