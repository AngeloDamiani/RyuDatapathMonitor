from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from operator import attrgetter
import threading
import time



class DatapathMonitor():
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, args):
        self.datapath_list = args["dp"]

        self.monitor = threading.Thread(target=self.switch_monitor_thread)
        self.delta = args["step"]
        self.logger = args["logger"]

        self.started = False

    def start(self):
        self.monitor.start()
        self.started = True

    def update(self, dplist):
        self.datapath_list = dplist


    def switch_monitor_thread(self):
        while True:
            time.sleep(self.delta)
            for datapath in self.datapath_list:
                self.logger.debug('Send stats request: %016x', datapath.id)
                ofproto = datapath.ofproto
                parser = datapath.ofproto_parser

                # I'm asking for all flows stats of the unique flow table in the switch
                req = parser.OFPFlowStatsRequest(datapath)
                datapath.send_msg(req)

                # I'm asking for all ports stats
                req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
                datapath.send_msg(req)

                # I'm asking for all descriptions and stats of queues of all active ports of datapath
                #req = parser.OFPQueueStatsRequest(datapath, 0, ofproto.OFPP_ANY,
                #                                      ofproto.OFPQ_ALL)
                #datapath.send_msg(req)

                #req = parser.OFPQueueGetConfigRequest(datapath, ofproto.OFPP_ANY)
                #datapath.send_msg(req)



    def flow_stats_reply(self, ev):
        body = ev.msg.body

        self.logger.info('datapath         '
                         'in-port  eth-dst           '
                         'out-port packets  bytes')
        self.logger.info('---------------- '
                         '-------- ----------------- '
                         '-------- -------- --------')
        for stat in sorted([flow for flow in body if flow.priority == 1],
                           key=lambda flow: (flow.match['in_port'],
                                             flow.match['eth_dst'])):
            self.logger.info('%016x %8x %17s %8x %8d %8d',
                             ev.msg.datapath.id,
                             stat.match['in_port'], stat.match['eth_dst'],
                             stat.instructions[0].actions[0].port,
                             stat.packet_count, stat.byte_count)

    def port_stats_reply(self, ev):
        body = ev.msg.body

        self.logger.info('datapath         port     '
                         'rx-pkts  rx-bytes rx-error '
                         'tx-pkts  tx-bytes tx-error')
        self.logger.info('---------------- -------- '
                         '-------- -------- -------- '
                         '-------- -------- --------')
        for stat in sorted(body, key=attrgetter('port_no')):
            self.logger.info('%016x %8x %8d %8d %8d %8d %8d %8d',
                             ev.msg.datapath.id, stat.port_no,
                             stat.rx_packets, stat.rx_bytes, stat.rx_errors,
                             stat.tx_packets, stat.tx_bytes, stat.tx_errors)

    def queue_stats_reply(self, ev):
        body = ev.msg.body

        self.logger.info('Datapath id     '
                         'Port number     '
                         'queue id         '
                         'tx bytes        '
                         'tx packets      '
                         'tx errors       ')
        self.logger.info('----------------'
                         '----------------'
                         '----------------'
                         '----------------'
                         '----------------'
                         '----------------')

        for stat in sorted(body, key=attrgetter('port_no')):
            self.logger.info('%016x %10x %12d %16d %17d %14d',
                             ev.msg.datapath.id, stat.port_no, stat.queue_id,
                              stat.tx_bytes, stat.tx_packets, stat.tx_errors)


    def queue_desc_reply(self, ev):
        body = ev.msg.body

        self.logger.info('Datapath id     '
                         'Port number     '
                         'queue id         '
                         'max rate        '
                         'min rate      ')
        self.logger.info('----------------'
                         '----------------'
                         '----------------'
                         '----------------'
                         '----------------')
        for queue in sorted(body, key=attrgetter('queues')):

            queue_id = queue.queue_id
            port = queue.port
            properties = queue.properties
            print(properties)
            #for prop in properties:


            #self.logger.info('%016x %10x %12d %16d %17d %14d',
            #                 ev.msg.datapath.id, stat.port_no, stat.queue_id,
            #                  stat.tx_bytes, stat.tx_packets, stat.tx_errors)