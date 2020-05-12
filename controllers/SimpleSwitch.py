
"""

We wrote this code, but relied heavily on the following sources for inspiration:

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
import collections


class SimpleSWitch(app_manager.RyuApp):

    OFP_VERSIONS = [
        ofproto_v1_3.OFP_VERSION,
        ofproto_v1_4.OFP_VERSION,
        ofproto_v1_0.OFP_VERSION,
        ofproto_v1_2.OFP_VERSION,
        ofproto_v1_5.OFP_VERSION
    ]

    def __init__(self, *args, **kwargs):

        super(SimpleSWitch, self).__init__(*args, **kwargs)

        self.logger.info(type(self).__name__ + " is initializing")
        
        self.mac_to_port = collections.defaultdict()  # used to learn MAC addr

        self.logger.info(type(self).__name__ + " has initialized")
    
    def do_we_know_mac(self, mac):
    
        return self.get_macs_port(mac) is not None
    
    def remember_mac(self, mac, port):
        
        if self.do_we_know_mac(mac) and self.mac_to_port[mac] == port:
            return
        
        self.mac_to_port[mac] = port

        self.logger.info("Remembering %s maps to port %s", mac, port)
        
    def get_macs_port(self, mac):
        
        if mac in self.mac_to_port:
            
            return self.mac_to_port[mac]
        
        return None
    
    # function template at https://ryu.readthedocs.io/en/latest/ofproto_v1_3_ref.html#modify-state-messages
    def send_flow_mod(self, datapath, match, actions, new_priority=0):
        
        self.logger.info("Begin send_flow_mod()")
        self.logger.info("Match: " + str(match))
        self.logger.info("Actions: " + str(actions))
        
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        # cookie = cookie_mask = 0
        # table_id = 0
        # idle_timeout = hard_timeout = 0
        priority = new_priority
        # buffer_id = ofp.OFP_NO_BUFFER
        inst = [
            ofp_parser.OFPInstructionActions(
                ofp.OFPIT_APPLY_ACTIONS,
                actions
            )
        ]
        
        # Build a flow modification message (or something)
        """
        req = ofp_parser.OFPFlowMod(
            datapath, cookie, cookie_mask,
            table_id, ofp.OFPFC_ADD,
            idle_timeout, hard_timeout,
            priority, buffer_id,
            ofp.OFPP_ANY, ofp.OFPG_ANY,
            ofp.OFPFF_SEND_FLOW_REM,
            match, inst
        )
        """
        req = ofp_parser.OFPFlowMod(
            datapath=datapath, priority=priority,
            match=match, instructions=inst
        )
        
        # self.logger.info("Sending message to our datapath: " + str(req))
        datapath.send_msg(req)

        # self.logger.info("End send_flow_mod()")
    
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def simple_switch_features_handler(self, ev):

        # self.logger.info("Begin simple_switch_features_handler")

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
        self.send_flow_mod(dp, match, actions)
        
        # self.logger.info("End simple_switch_features_handler")
    
    # sends received packets to all ports
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        
        # self.logger.info("Begin packet_in_handler")
        
        msg = ev.msg  # instance of OpenFlow messages
        # self.logger.info("Got message: " + str(msg))
        
        # represent a datapath(switch) which corresponding to OpenFlow that issued the message
        dp = msg.datapath
        # self.logger.info("Got datapath: " + str(dp))
        
        ofp = dp.ofproto  # the protocol that Openflow version in use
        ofp_parser = dp.ofproto_parser

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        # print(pkt)

        src_mac = eth.src
        dst_mac = eth.dst
        # self.logger.info("Packet is flowing from %s to %s", src, dst)
        
        in_port = msg.match['in_port']
        # self.logger.info("Packet is coming in on port: " + str(in_port))
        
        self.remember_mac(src_mac, in_port)
        
        # Try to figure out what port to send the packet out on
        if self.do_we_know_mac(dst_mac):
            # self.logger.info("We already knew this port")
            out_port = self.get_macs_port(dst_mac)
        else:
            self.logger.info("Didn't know where " + dst_mac + " is plugged in")
            out_port = ofp.OFPP_FLOOD
        
        # construct packet_out message and send it.
        actions = [ofp_parser.OFPActionOutput(out_port)]
        
        # switch already knew this port, modify table flow to avoid packet_in next time
        if out_port != ofp.OFPP_FLOOD:
            
            # self.logger.info("Trying to modify the table flow to avoid packet_in next time")
            match = ofp_parser.OFPMatch(in_port=in_port, eth_dst=dst_mac)
            self.send_flow_mod(dp, match, actions, 1)
        
        # Switch didn't already know this port
        else:
            # self.logger.info("Switch didn't already know destination " + str(dst) + " mapped to port " + str(out_port))
            # self.logger.info("Mac-to-Port dictionary looks like: " + str(self.mac_to_port))
            pass
        
        out = ofp_parser.OFPPacketOut(
            datapath=dp,
            buffer_id=ofp.OFP_NO_BUFFER,
            in_port=in_port, actions=actions,
            data=msg.data
        )
        dp.send_msg(out)

        # self.logger.info("End packet_in_handler")
