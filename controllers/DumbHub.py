

"""

We wrote this code, but relied heaviliy on the following sources for inspiration:

1. https://osrg.github.io/ryu-book/en/html/switching_hub.html#adding-table-miss-flow-entry
2. https://ryu.readthedocs.io/en/latest/writing_ryu_app.html
3. https://github.com/osrg/ryu/blob/master/ryu/app/simple_switch.py
4. https://ryu.readthedocs.io/en/latest/ofproto_v1_3_ref.html#modify-state-messages
5. https://ryu.readthedocs.io/en/latest/ofproto_v1_3_ref.html

Please keep the above admission fully in mind if you see any similarities :)

"""

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import HANDSHAKE_DISPATCHER, MAIN_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3, ofproto_v1_0, ofproto_v1_2, ofproto_v1_4, ofproto_v1_5
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
# from ryu.lib.packet import ether_types
# from ryu.lib.mac import haddr_to_bin


class DumbHub(app_manager.RyuApp):
    
    OFP_VERSIONS = [
        ofproto_v1_3.OFP_VERSION,
        ofproto_v1_4.OFP_VERSION,
        ofproto_v1_0.OFP_VERSION,
        ofproto_v1_2.OFP_VERSION,
        ofproto_v1_5.OFP_VERSION
    ]
    
    def __init__(self, *args, **kwargs):
        
        super(DumbHub, self).__init__(*args, **kwargs)
        
        self.mac_to_port = {}
        self.logger.info('***DumbHub***')

    # function template at https://ryu.readthedocs.io/en/latest/ofproto_v1_3_ref.html#modify-state-messages
    def send_flow_mod(self, datapath, match, actions):
        
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        cookie = cookie_mask = 0
        table_id = 0
        idle_timeout = hard_timeout = 0
        priority = 32768
        buffer_id = ofp.OFP_NO_BUFFER
        inst = [
            ofp_parser.OFPInstructionActions(
                ofp.OFPIT_APPLY_ACTIONS,
                actions
            )
        ]
        req = ofp_parser.OFPFlowMod(
            datapath, cookie, cookie_mask,
            table_id, ofp.OFPFC_ADD,
            idle_timeout, hard_timeout,
            priority, buffer_id,
            ofp.OFPP_ANY, ofp.OFPG_ANY,
            ofp.OFPFF_SEND_FLOW_REM,
            match, inst
        )
        datapath.send_msg(req)
    
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def dumb_hub_features_handler(self, ev):
        
        self.logger.info('****dumb_hub_handler****')
        
        dp = ev.msg.datapath
        ofproto = dp.ofproto
        ofp_parser = dp.ofproto_parser
        
        msg = ev.msg

        match = ofp_parser.OFPMatch()  # match all packets
        actions = [
            ofp_parser.OFPActionOutput(
                ofproto.OFPP_CONTROLLER,
                ofproto.OFPCML_NO_BUFFER
            )
        ]
        # print(match)
        # print(actions)
        self.send_flow_mod(dp, match, actions)

    # sends received packets to all ports
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        
        self.logger.info("***packet_in_handler***")
        
        msg = ev.msg  # instance of OpenFlow messages
        # represent a datapath(switch) which corresponding to OpenFlow that issued the message
        dp = msg.datapath
        ofp = dp.ofproto  # the protocol that Openflow version in use
        ofp_parser = dp.ofproto_parser

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        # print(pkt)

        dst = eth.dst
        src = eth.src

        # in_port = msg.match('in_port')
        # print(msg)
        in_port = msg.match['in_port']
        # print('in_port' + str(in_port))

        dpid = dp.id
        self.mac_to_port.setdefault(dpid, {})
        self.logger.info("packet in %s %s %s", dpid, src, dst)

        self.mac_to_port[dpid][src] = in_port

        # construct packet_out message and send it.
        actions = [ofp_parser.OFPActionOutput(ofp.OFPP_FLOOD)]
        out = ofp_parser.OFPPacketOut(
            datapath=dp,
            buffer_id=ofp.OFP_NO_BUFFER,
            in_port=in_port, actions=actions,
            data=msg.data
        )
        dp.send_msg(out)
