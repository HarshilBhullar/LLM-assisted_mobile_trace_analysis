
#!/usr/bin/python
# Filename: modified_lte_mac_analyzer.py

from mobile_insight.analyzer.analyzer import Analyzer
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

    def set_source(self, source):
        Analyzer.set_source(self, source)

        source.enable_log("LTE_MAC_UL_Tx_Statistics")
        source.enable_log("LTE_MAC_UL_Buffer_Status_Internal")
        source.enable_log("LTE_PHY_PDSCH_Stat_Indication")

    def __msg_callback(self, msg):

        if msg.type_id == "LTE_MAC_UL_Tx_Statistics":
            log_item = msg.data.decode()

            grant_received = 0
            grant_utilized = 0
            grant_utilization = 0

            for i in range(0, len(log_item['Subpackets'])):
                grant_received += log_item['Subpackets'][i]['Sample']['Grant received']
                grant_utilized += log_item['Subpackets'][i]['Sample']['Grant utilized']

            if grant_received != 0:
                grant_utilization = round(
                    100.0 * (grant_utilized) / grant_received, 2)
                bcast_dict = {}
                bcast_dict['timestamp'] = str(log_item['timestamp'])
                bcast_dict['received'] = str(grant_received)
                bcast_dict['used'] = str(grant_utilized)
                bcast_dict['utilization'] = str(grant_utilization)
                self.broadcast_info("MODIFIED_MAC_UL_GRANT", bcast_dict)
                self.log_info(str(log_item['timestamp']) +
                              " Modified MAC UL grant: received=" +
                              str(grant_received) +
                              " bytes" +
                              " used=" +
                              str(grant_utilized) +
                              " bytes" +
                              " utilization=" +
                              str(grant_utilization) +
                              "%")

        elif msg.type_id == "LTE_MAC_UL_Buffer_Status_Internal":
            log_item = msg.data.decode()
            if 'Subpackets' in log_item:
                for i in range(0, len(log_item['Subpackets'])):
                    if 'Samples' in log_item['Subpackets'][i]:
                        for sample in log_item['Subpackets'][i]['Samples']:
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
                                break

                            for lcid in sample['LCIDs']:
                                try:
                                    idx = lcid['Ld Id']
                                    new_bytes = int(lcid['New Compressed Bytes'])
                                    ctrl_bytes = int(lcid['Ctrl bytes'])
                                    total_bytes = int(lcid['Total Bytes'])
                                except KeyError:
                                    continue

                                if idx not in self.buffer:
                                    self.buffer[idx] = []
                                if idx not in self.last_bytes:
                                    self.last_bytes[idx] = 0
                                if idx not in self.ctrl_pkt_sfn:
                                    self.ctrl_pkt_sfn[idx] = None

                                if not new_bytes == 0:
                                    if new_bytes > self.last_bytes[idx]:
                                        new_bytes = new_bytes - self.last_bytes[idx]
                                        self.buffer[idx].append([(self.cur_fn[0], self.cur_fn[1]), new_bytes])

                                if not ctrl_bytes == 0:
                                    total_bytes -= 2
                                    if not self.ctrl_pkt_sfn[idx]:
                                        self.ctrl_pkt_sfn[idx] = (self.cur_fn[0], self.cur_fn[1])
                                else:
                                    if self.ctrl_pkt_sfn[idx]:
                                        ctrl_pkt_delay = self.cur_fn[0] * 10 + self.cur_fn[1] \
                                                         - self.ctrl_pkt_sfn[idx][0] * 10 - self.ctrl_pkt_sfn[idx][1]
                                        ctrl_pkt_delay += 10240 if ctrl_pkt_delay < 0 else 0
                                        self.ctrl_pkt_sfn[idx] = None
                                        self.log_info(str(log_item['timestamp']) + " MODIFIED_UL_CTRL_PKT_DELAY: " + str(ctrl_pkt_delay))
                                        bcast_dict = {}
                                        bcast_dict['timestamp'] = str(log_item['timestamp'])
                                        bcast_dict['delay'] = str(ctrl_pkt_delay)
                                        self.broadcast_info("MODIFIED_UL_CTRL_PKT_DELAY", bcast_dict)

                                if self.last_bytes[idx] > total_bytes:
                                    sent_bytes = self.last_bytes[idx] - total_bytes
                                    while len(self.buffer[idx]) > 0 and sent_bytes > 0:
                                        pkt = self.buffer[idx][0]
                                        if pkt[1] <= sent_bytes:
                                            pkt_delay = self.cur_fn[0] * 10 + self.cur_fn[1] \
                                                             - pkt[0][0] * 10 - pkt[0][1]
                                            pkt_delay += 10240 if pkt_delay < 0 else 0
                                            self.buffer[idx].pop(0)
                                            sent_bytes -= pkt[1]
                                            self.log_info(str(log_item['timestamp']) + " MODIFIED_UL_PKT_DELAY: " + str(pkt_delay))
                                            bcast_dict = {}
                                            bcast_dict['timestamp'] = str(log_item['timestamp'])
                                            bcast_dict['delay'] = str(pkt_delay)
                                            self.broadcast_info("MODIFIED_UL_PKT_DELAY", bcast_dict)
                                        else:
                                            pkt[1] -= sent_bytes
                                self.last_bytes[idx] = total_bytes
                            queue_length = 0
                            for idx in self.last_bytes:
                                queue_length += self.last_bytes[idx]
                                if queue_length > 0 and queue_length != self.queue_length:
                                    self.queue_length = queue_length
                                    self.log_info(str(log_item['timestamp']) + " MODIFIED_UL_QUEUE_LENGTH: " + str(queue_length))
                                    bcast_dict = {}
                                    bcast_dict['timestamp'] = str(log_item['timestamp'])
                                    bcast_dict['length'] = str(queue_length)
                                    self.broadcast_info("MODIFIED_UL_QUEUE_LENGTH", bcast_dict)

        elif msg.type_id == "LTE_PHY_PDSCH_Stat_Indication":
            self.__msg_callback_pdsch_stat(msg)

    def __msg_callback_pdsch_stat(self, msg):
        log_item = msg.data.decode()
        timestamp = str(log_item['timestamp'])
        if 'Records' in log_item:
            for i in range(0, len(log_item['Records'])):
                record = log_item['Records'][i]
                if 'Transport Blocks' in record:
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
                    for blocks in log_item['Records'][i]['Transport Blocks']:
                        harq_id = int(blocks['HARQ ID'])
                        tb_idx = int(blocks['TB Index'])
                        is_retx = True if blocks['Did Recombining'][-2:] == "es" else False
                        crc_check = True if blocks['CRC Result'][-2:] == "ss" else False
                        tb_size = int(blocks['TB Size'])
                        rv_value = int(blocks['RV'])
                        rlc_retx = 0

                        id = harq_id + cell_idx * 8 + tb_idx * 24

                        if not crc_check:
                            cur_fail = [timestamp, cell_idx, harq_id, tb_idx, tb_size, False, 0, False, sn_sfn]
                            if self.failed_harq[id] != 0:
                                if rv_value > 0:
                                    self.failed_harq[id][6] += 1
                                else:
                                    self.failed_harq[id][-2] = True
                                    delay = sn_sfn - self.failed_harq[id][-1]
                                    bcast_dict = {}
                                    bcast_dict['pkt size'] = self.failed_harq[id][4]
                                    bcast_dict['timestamp'] = timestamp
                                    bcast_dict['delay'] = delay
                                    self.broadcast_info('MODIFIED_RLC_RETX', bcast_dict)
                                    self.log_info('MODIFIED_RLC_RETX: ' + str(bcast_dict))
                                    self.failed_harq[id] = 0
                            elif rv_value == 0:
                                self.failed_harq[id] = cur_fail

                        else:
                            if self.failed_harq[id] != 0:
                                if rv_value > 0 or is_retx:
                                    self.failed_harq[id][6] += 1
                                    self.failed_harq[id][-4] = True
                                    delay = sn_sfn - self.failed_harq[id][-1]
                                    bcast_dict = {}
                                    bcast_dict['pkt size'] = self.failed_harq[id][4]
                                    bcast_dict['timestamp'] = timestamp
                                    bcast_dict['delay'] = delay
                                    self.broadcast_info('MODIFIED_MAC_RETX', bcast_dict)
                                    self.log_info('MODIFIED_MAC_RETX: ' + str(bcast_dict))
                                else:
                                    self.failed_harq[id][-2] = True
                                    delay = sn_sfn - self.failed_harq[id][-1]
                                    bcast_dict = {}
                                    bcast_dict['pkt size'] = self.failed_harq[id][4]
                                    bcast_dict['timestamp'] = timestamp
                                    bcast_dict['delay'] = delay
                                    self.broadcast_info('MODIFIED_RLC_RETX', bcast_dict)
                                    self.log_info('MODIFIED_RLC_RETX: ' + str(bcast_dict))
                                self.failed_harq[id] = 0
