
#!/usr/bin/python
# Filename: modified_lte_mac_analyzer.py
"""
A comprehensive 4G MAC-layer analyzer with additional metrics

Author: Yuanjie Li, Modified by [Your Name]
"""

from mobile_insight.analyzer.analyzer import *
import datetime

__all__ = ["ModifiedLteMacAnalyzer"]

class ModifiedLteMacAnalyzer(Analyzer):

    def __init__(self):
        Analyzer.__init__(self)

        self.add_source_callback(self.__msg_callback)
        self.last_bytes = {}
        self.buffer = {}
        self.ctrl_pkt_sfn = {}
        self.cur_fn = None
        self.cell_id = {}
        self.idx = 0
        self.failed_harq = [0] * 8 * 3 * 2
        self.queue_length = 0
        self.total_grants_received = 0
        self.total_grants_utilized = 0

    def set_source(self, source):
        Analyzer.set_source(self, source)
        source.enable_log("LTE_MAC_UL_Tx_Statistics")
        source.enable_log("LTE_MAC_UL_Buffer_Status_Internal")
        source.enable_log("LTE_PHY_PDSCH_Stat_Indication")

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_MAC_UL_Tx_Statistics":
            self.__process_mac_ul_tx_statistics(msg)
        elif msg.type_id == "LTE_MAC_UL_Buffer_Status_Internal":
            self.__process_mac_ul_buffer_status_internal(msg)
        elif msg.type_id == "LTE_PHY_PDSCH_Stat_Indication":
            self.__msg_callback_pdsch_stat(msg)

    def __process_mac_ul_tx_statistics(self, msg):
        log_item = msg.data.decode()
        grant_received = 0
        grant_utilized = 0

        for subpkt in log_item['Subpackets']:
            grant_received += subpkt['Sample']['Grant received']
            grant_utilized += subpkt['Sample']['Grant utilized']

        if grant_received != 0:
            utilization = round(100.0 * grant_utilized / grant_received, 2)
            self.total_grants_received += grant_received
            self.total_grants_utilized += grant_utilized

            bcast_dict = {
                'timestamp': str(log_item['timestamp']),
                'received': str(grant_received),
                'used': str(grant_utilized),
                'utilization': str(utilization)
            }
            self.broadcast_info("MAC_UL_GRANT", bcast_dict)
            self.log_info(f"{log_item['timestamp']} MAC UL grant: received={grant_received} bytes, used={grant_utilized} bytes, utilization={utilization}%")

    def __process_mac_ul_buffer_status_internal(self, msg):
        log_item = msg.data.decode()
        if 'Subpackets' in log_item:
            for subpkt in log_item['Subpackets']:
                if 'Samples' in subpkt:
                    for sample in subpkt['Samples']:
                        self.__update_buffer_status(sample, log_item['timestamp'])

    def __update_buffer_status(self, sample, timestamp):
        sub_fn = int(sample['Sub FN'])
        sys_fn = int(sample['Sys FN'])

        if not (sys_fn >= 1023 and sub_fn >= 9):
            if self.cur_fn:
                lag = sys_fn * 10 + sub_fn - self.cur_fn[0] * 10 - self.cur_fn[1]
                if lag > 2 or -10238 < lag < 0:
                    self.last_bytes = {}
                    self.buffer = {}
                    self.ctrl_pkt_sfn = {}
            self.cur_fn = [sys_fn, sub_fn]
        elif self.cur_fn:
            self.cur_fn[1] += 1
            if self.cur_fn[1] == 10:
                self.cur_fn[1] = 0
                self.cur_fn[0] += 1
            if self.cur_fn[0] == 1024:
                self.cur_fn = [0, 0]

        if not self.cur_fn:
            return

        for lcid in sample['LCIDs']:
            self.__process_lcid(lcid, timestamp)

    def __process_lcid(self, lcid, timestamp):
        try:
            idx = lcid['Ld Id']
            new_bytes = int(lcid['New Compressed Bytes'])
            ctrl_bytes = int(lcid['Ctrl bytes'])
            total_bytes = int(lcid['Total Bytes'])
        except KeyError:
            return

        if idx not in self.buffer:
            self.buffer[idx] = []
        if idx not in self.last_bytes:
            self.last_bytes[idx] = 0
        if idx not in self.ctrl_pkt_sfn:
            self.ctrl_pkt_sfn[idx] = None

        if not new_bytes == 0:
            if new_bytes > self.last_bytes[idx]:
                new_bytes -= self.last_bytes[idx]
                self.buffer[idx].append([(self.cur_fn[0], self.cur_fn[1]), new_bytes])

        if not ctrl_bytes == 0:
            total_bytes -= 2
            if not self.ctrl_pkt_sfn[idx]:
                self.ctrl_pkt_sfn[idx] = (self.cur_fn[0], self.cur_fn[1])
        else:
            if self.ctrl_pkt_sfn[idx]:
                ctrl_pkt_delay = self.cur_fn[0] * 10 + self.cur_fn[1] - self.ctrl_pkt_sfn[idx][0] * 10 - self.ctrl_pkt_sfn[idx][1]
                ctrl_pkt_delay += 10240 if ctrl_pkt_delay < 0 else 0
                self.ctrl_pkt_sfn[idx] = None
                self.log_info(f"{timestamp} UL_CTRL_PKT_DELAY: {ctrl_pkt_delay}")
                bcast_dict = {'timestamp': timestamp, 'delay': str(ctrl_pkt_delay)}
                self.broadcast_info("UL_CTRL_PKT_DELAY", bcast_dict)

        if self.last_bytes[idx] > total_bytes:
            sent_bytes = self.last_bytes[idx] - total_bytes
            while len(self.buffer[idx]) > 0 and sent_bytes > 0:
                pkt = self.buffer[idx][0]
                if pkt[1] <= sent_bytes:
                    pkt_delay = self.cur_fn[0] * 10 + self.cur_fn[1] - pkt[0][0] * 10 - pkt[0][1]
                    pkt_delay += 10240 if pkt_delay < 0 else 0
                    self.buffer[idx].pop(0)
                    sent_bytes -= pkt[1]
                    self.log_info(f"{timestamp} UL_PKT_DELAY: {pkt_delay}")
                    bcast_dict = {'timestamp': timestamp, 'delay': str(pkt_delay)}
                    self.broadcast_info("UL_PKT_DELAY", bcast_dict)
                else:
                    pkt[1] -= sent_bytes
        self.last_bytes[idx] = total_bytes

        queue_length = sum(self.last_bytes.values())
        if queue_length > 0 and queue_length != self.queue_length:
            self.queue_length = queue_length
            self.log_info(f"{timestamp} UL_QUEUE_LENGTH: {queue_length}")
            bcast_dict = {'timestamp': timestamp, 'length': str(queue_length)}
            self.broadcast_info("UL_QUEUE_LENGTH", bcast_dict)

    def __msg_callback_pdsch_stat(self, msg):
        log_item = msg.data.decode()
        timestamp = str(log_item['timestamp'])
        if 'Records' in log_item:
            for record in log_item['Records']:
                if 'Transport Blocks' in record:
                    self.__process_transport_blocks(record, timestamp)

    def __process_transport_blocks(self, record, timestamp):
        if 'Serving Cell Index' in record:
            cell_id_str = record['Serving Cell Index']
            if cell_id_str not in self.cell_id:
                self.cell_id[cell_id_str] = self.idx
                cell_idx = self.idx
                self.idx += 1
            else:
                cell_idx = self.cell_id[cell_id_str]
            sn = int(record['Frame Num'])
            sfn = int(record['Subframe Num'])
            sn_sfn = sn * 10 + sfn
        for blocks in record['Transport Blocks']:
            harq_id = int(blocks['HARQ ID'])
            tb_idx = int(blocks['TB Index'])
            is_retx = blocks['Did Recombining'][-2:] == "es"
            crc_check = blocks['CRC Result'][-2:] == "ss"
            tb_size = int(blocks['TB Size'])
            rv_value = int(blocks['RV'])

            id = harq_id + cell_idx * 8 + tb_idx * 24

            if not crc_check:
                cur_fail = [timestamp, cell_idx, harq_id, tb_idx, tb_size, False, 0, False, sn_sfn]
                if self.failed_harq[id] != 0:
                    if rv_value > 0:
                        self.failed_harq[id][6] += 1
                    else:
                        self.failed_harq[id][-2] = True
                        delay = sn_sfn - self.failed_harq[id][-1]
                        bcast_dict = {'pkt size': self.failed_harq[id][4], 'timestamp': timestamp, 'delay': delay}
                        self.broadcast_info('RLC_RETX', bcast_dict)
                        self.log_info(f'RLC_RETX: {bcast_dict}')
                        self.failed_harq[id] = 0
                elif rv_value == 0:
                    self.failed_harq[id] = cur_fail

            else:
                if self.failed_harq[id] != 0:
                    if rv_value > 0 or is_retx:
                        self.failed_harq[id][6] += 1
                        self.failed_harq[id][-4] = True
                        delay = sn_sfn - self.failed_harq[id][-1]
                        bcast_dict = {'pkt size': self.failed_harq[id][4], 'timestamp': timestamp, 'delay': delay}
                        self.broadcast_info('MAC_RETX', bcast_dict)
                        self.log_info(f'MAC_RETX: {bcast_dict}')
                    else:
                        self.failed_harq[id][-2] = True
                        delay = sn_sfn - self.failed_harq[id][-1]
                        bcast_dict = {'pkt size': self.failed_harq[id][4], 'timestamp': timestamp, 'delay': delay}
                        self.broadcast_info('RLC_RETX', bcast_dict)
                        self.log_info(f'RLC_RETX: {bcast_dict}')
                    self.failed_harq[id] = 0
