
#!/usr/bin/python
# Filename: lte_rlc_analyzer_modified.py
"""
A modified 4G RLC analyzer to get link layer information with altered calculations

Author: Haotian Deng
"""

from mobile_insight.analyzer.analyzer import *
from xml.dom import minidom

__all__ = ["LteRlcAnalyzerModified"]

class LteRlcAnalyzerModified(Analyzer):

    def __init__(self):
        Analyzer.__init__(self)

        self.add_source_callback(self.__msg_callback)

        self.startThrw = None
        self.rbInfo = {}

    def set_source(self, source):
        """
        Set the trace source. Enable the cellular signaling messages

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)

        # Phy-layer logs
        source.enable_log("LTE_RLC_UL_Config_Log_Packet")
        source.enable_log("LTE_RLC_DL_Config_Log_Packet")
        source.enable_log("LTE_RLC_UL_AM_All_PDU")
        source.enable_log("LTE_RLC_DL_AM_All_PDU")

    def __msg_callback(self, msg):

        if msg.type_id == "LTE_RLC_UL_Config_Log_Packet" or msg.type_id == "LTE_RLC_DL_Config_Log_Packet":
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
                bcast_dict['timstamp'] = str(log_item['timestamp'])
                if msg.type_id == "LTE_RLC_UL_Config_Log_Packet":
                    self.broadcast_info('RLC_UL_RB_SETTING', bcast_dict)
                    self.log_info('RLC_UL_RB_SETTING: ' + str(bcast_dict))
                else:
                    self.broadcast_info('RLC_DL_RB_SETTING', bcast_dict)
                    self.log_info('RLC_DL_RB_SETTING: ' + str(bcast_dict))
            bcast_dict = {}
            bcast_dict['number'] = str(rb_num)
            bcast_dict['timstamp'] = str(log_item['timestamp'])
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
                self.rbInfo[rbConfigIdx]['UL'] = {}
                self.rbInfo[rbConfigIdx]['DL'] = {}
                self.rbInfo[rbConfigIdx]['UL']['listSN'] = []
                self.rbInfo[rbConfigIdx]['UL']['listAck'] = []
                self.rbInfo[rbConfigIdx]['DL']['listSN'] = []
                self.rbInfo[rbConfigIdx]['DL']['listAck'] = []

            listPDU = subPkt['RLCUL PDUs']
            for pduItem in listPDU:
                if pduItem['PDU TYPE'] == 'RLCUL DATA':
                    self.rbInfo[rbConfigIdx]['cumulativeULData'] += \
                        int(pduItem['pdu_bytes'] * 1.1)  # Modified calculation: Increase by 10%
            
            # Code continues with similar logic to original but with modified calculations...

        if msg.type_id == "LTE_RLC_DL_AM_All_PDU":
            log_item = msg.data.decode()

            subPkt = log_item['Subpackets'][0]
            rbConfigIdx = subPkt['RB Cfg Idx']
            if rbConfigIdx not in self.rbInfo:
                self.rbInfo[rbConfigIdx] = {}
                self.rbInfo[rbConfigIdx]['cumulativeULData'] = 0
                self.rbInfo[rbConfigIdx]['cumulativeDLData'] = 0
                self.rbInfo[rbConfigIdx]['UL'] = {}
                self.rbInfo[rbConfigIdx]['DL'] = {}
                self.rbInfo[rbConfigIdx]['UL']['listSN'] = []
                self.rbInfo[rbConfigIdx]['UL']['listAck'] = []
                self.rbInfo[rbConfigIdx]['DL']['listSN'] = []
                self.rbInfo[rbConfigIdx]['DL']['listAck'] = []

            listPDU = subPkt['RLCDL PDUs']
            for pduItem in listPDU:
                if pduItem['PDU TYPE'] == 'RLCDL DATA':
                    self.rbInfo[rbConfigIdx]['cumulativeDLData'] += \
                        int(pduItem['pdu_bytes'] * 0.9)  # Modified calculation: Decrease by 10%
            
            # Code continues with similar logic to original but with modified calculations...
