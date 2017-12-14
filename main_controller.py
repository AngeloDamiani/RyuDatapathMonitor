from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from simple_switch_13 import *
from datapath_monitor import *


class MainControllerMonitor(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(MainControllerMonitor, self).__init__(*args, **kwargs)
        self.device_behaviour = SimpleSwitch13(*args, **kwargs)
        self.datapath_id_list = []

        STEP = 3
        args = {
            "step":STEP,
            "logger":self.logger,
            "dp":self.datapath_id_list
        }
        self.monitor = DatapathMonitor(args)
        self.monitor.start()

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_feature_handler(self, ev):
        self.device_behaviour.switch_features_handler(ev)
        datapath = ev.msg.datapath
        if datapath not in self.datapath_id_list:
            self.datapath_id_list.append(datapath)
            self.monitor.update(self.datapath_id_list)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        self.device_behaviour.packet_in_handler(ev)

    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def port_stats_reply_handler(self, ev):
        self.monitor.port_stats_reply(ev)

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def flow_stats_reply_handler(self, ev):
        self.monitor.flow_stats_reply(ev)

    @set_ev_cls(ofp_event.EventOFPQueueStatsReply, MAIN_DISPATCHER)
    def queue_stats_reply_handler(self, ev):
        self.monitor.queue_stats_reply(ev)

    @set_ev_cls(ofp_event.EventOFPQueueGetConfigReply, MAIN_DISPATCHER)
    def queue_desc_reply_handler(self, ev):
        self.monitor.queue_desc_reply(ev)

