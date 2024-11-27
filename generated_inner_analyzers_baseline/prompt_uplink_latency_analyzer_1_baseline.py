
from mobile_insight.analyzer.analyzer import Analyzer

class ModifiedUplinkLatencyAnalyzer(Analyzer):
    def __init__(self):
        super(ModifiedUplinkLatencyAnalyzer, self).__init__()
        self.fn = 0
        self.sfn = 0
        self.cum_err_block = [0]
        self.cum_block = [0]
        self.mac_buffer = []
        self.all_packets = []
        self.transmitted_packets = []
        self.temp_dict = {}

    def set_source(self, source):
        source.enable_log("LTE_PHY_PUSCH_Tx_Report")
        source.enable_log("LTE_MAC_UL_Buffer_Status_Internal")
        self.source = source

    def __msg_callback(self, msg):
        if msg.type_id == "LTE_PHY_PUSCH_Tx_Report":
            self.__process_pusch_tx_report(msg)
        elif msg.type_id == "LTE_MAC_UL_Buffer_Status_Internal":
            self.__process_mac_ul_buffer_status(msg)

    def __process_pusch_tx_report(self, msg):
        data = msg.data.decode()
        for record in data['Records']:
            fn = record['Frame Number']
            sfn = record['Subframe Number']
            block = record['Block']
            retransmission = record['Retransmission']
            
            self.update_time(fn, sfn)
            current_time = self.__f_time()

            if block not in self.temp_dict:
                self.temp_dict[block] = {
                    'Start Time': current_time,
                    'Retransmission': retransmission,
                    'Waiting Latency': 0,
                    'Tx Latency': 0,
                    'Retx Latency': 0
                }
            else:
                self.cum_err_block[0] += 1
                previous_time = self.temp_dict[block]['Start Time']
                self.temp_dict[block]['Retx Latency'] = self.__f_time_diff(previous_time, current_time)

            self.cum_block[0] += 1
            self.transmitted_packets.append(self.temp_dict[block])
            del self.temp_dict[block]

    def __process_mac_ul_buffer_status(self, msg):
        data = msg.data.decode()
        for report in data['Reports']:
            buf_status = report['Buffer Status']
            if buf_status > 0:
                self.mac_buffer.append({
                    'fn': self.fn,
                    'sfn': self.sfn,
                    'buf_status': buf_status
                })

        self.__cmp_queues()

    def __f_time_diff(self, start_time, end_time):
        return (end_time - start_time) % 10240

    def __f_time(self):
        return self.fn * 10 + self.sfn

    def __cmp_queues(self):
        for packet in self.transmitted_packets:
            if packet['Retransmission']:
                continue

            for buffer in self.mac_buffer:
                if buffer['buf_status'] > 0:
                    waiting_time = self.__f_time_diff(buffer['fn'] * 10 + buffer['sfn'], packet['Start Time'])
                    packet['Waiting Latency'] = waiting_time
                    self.all_packets.append(packet)
                    self.mac_buffer.remove(buffer)
                    break

    def update_time(self, fn, sfn):
        self.fn = fn
        self.sfn = sfn
