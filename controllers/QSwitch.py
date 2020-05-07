# https://github.com/osrg/ryu/blob/master/ryu/app/simple_monitor_13.py
# https://github.com/knetsolutions/learn-sdn-with-ryu/blob/master/ryu_part4.md
# https://ryu.readthedocs.io/en/latest/library_packet.html

# from SimpleSwitch import *
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.lib.packet import packet, tcp, udp, ipv4, ipv6, in_proto, ethernet, stream_parser
from ryu.controller.handler import HANDSHAKE_DISPATCHER, MAIN_DISPATCHER, CONFIG_DISPATCHER
from ryu.ofproto import ofproto_v1_3, ofproto_v1_0, ofproto_v1_2, ofproto_v1_4, ofproto_v1_5
from ryu.controller.handler import set_ev_cls
from ryu.lib.packet import ether_types
import array
import collections


class QSwitch(app_manager.RyuApp):
    OFP_VERSIONS = [
        ofproto_v1_3.OFP_VERSION,
        ofproto_v1_4.OFP_VERSION,
        ofproto_v1_0.OFP_VERSION,
        ofproto_v1_2.OFP_VERSION,
        ofproto_v1_5.OFP_VERSION
    ]
    def __init__(self, *args, **kwargs):

        super(QSwitch, self).__init__(*args, **kwargs)
        self.logger.info('***QSwitch***')
        self.mac_to_port = collections.defaultdict()

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

    def send_flow_mod(self, datapath, match, actions, new_priority=0, new_buffer_id=None):

        self.logger.info("Begin send_flow_mod()")
        self.logger.info("Actions: " + str(actions))

        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser
        
        cookie = cookie_mask = 0
        table_id = 0
        idle_timeout = hard_timeout = 0
        priority = new_priority
        buffer_id = [new_buffer_id if new_buffer_id else ofp.OFP_NO_BUFFER][0]
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
            match=match, instructions=inst,
            buffer_id=buffer_id
        )

        self.logger.info("Sending message to our datapath: " + str(req))
        datapath.send_msg(req)
        
        self.logger.info("End send_flow_mod")

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def qswitch_features_handler(self, ev):

        # self.logger.info("Begin q_switch_features_handler")

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
        self.send_flow_mod(dp, match, actions, 0, ofproto.OFP_NO_BUFFER)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        
        # Blehhhh
        self.logger.info("")
        self.logger.info("Begin the packet_in_handler")
        
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
            self.logger.info("Didn't know where " + dst_mac + " is plugged in; Will flood")
            out_port = ofp.OFPP_FLOOD

        # construct packet_out message and send it.
        actions = [ofp_parser.OFPActionOutput(out_port)]
        
        # switch already knew this port, modify table flow to avoid packet_in next time
        if out_port != ofp.OFPP_FLOOD:
            
            self.logger.info("Didn't flood; Trying to modify the table flow to avoid packet_in next time")
            self.logger.info("Packet is flowing from %s to %s", src_mac, dst_mac)
            
            # match = ofp_parser.OFPMatch(in_port=in_port, eth_dst=dst_mac)
            # self.send_flow_mod(dp, match, actions, 1)

            # pkt = packet.Packet(array.array('B', ev.msg.data))
            # self.logger.info(pkt)
            # print(pkt.get_protocol(ipv6))
            # self.logger.info(pkt.get_protocol(ipv6))
            # ip6 = pkt.get_protocol(ipv6.ipv6)
            # self.logger.info('ipv6 %s', ip6)
            # self.logger.info(ip6.nxt)
            # eth = pkt.get_protocols(ethernet.ethernet)
            # self.logger.info('ethernet %s', eth)

            # ip4 = pkt.get_protocol(ipv4.ipv4)
            # self.logger.info('ipv4: %s', ip4)

            # tcp_pkt = tcp.tcp(bits=(tcp.TCP_SYN | tcp.TCP_ACK))
            # self.logger.info(tcp_pkt)
            # x = pkt.get_protocol(tcp.tcp)
            # self.logger.info(x)

            # eth = pkt.get_protocol(ethernet.ethernet)
            # self.logger.info(eth)
            # self.logger.info('Ethernet Type: %s', eth.ethertype)
            # self.logger.info('IP Type: %s', ether_types.ETH_TYPE_IP)

            # inspired from https://github.com/knetsolutions/learn-sdn-with-ryu/blob/master/ryu-exercises/ex3_L4Match_switch.py
            if eth.ethertype == ether_types.ETH_TYPE_IP:
    
                self.logger.info("Got an IP type of ether packet")
                
                ip4 = pkt.get_protocol(ipv4.ipv4)
                
                self.logger.info('ipv4: %s', ip4)
                
                ip4_scr = ip4.src
                ip4_dst = ip4.dst
                protocol = ip4.proto
                # self.logger.info(in_proto)
                t = u = None
                if protocol == in_proto.IPPROTO_TCP:
                    self.logger.info('This packet is using TCP!')
                    t = pkt.get_protocol(tcp.tcp)
                    match = ofp_parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP, ipv4_src=ip4.src, ipv4_dst=ip4.dst, ip_proto=protocol, tcp_src=t.src_port, tcp_dst=t.dst_port)
                elif protocol == in_proto.IPPROTO_ICMP:
                    match = ofp_parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP, ipv4_src=ip4.src, ipv4_dst=ip4.dst, ip_proto=protocol)
                elif protocol == in_proto.IPPROTO_UDP:
                    self.logger.info('This packet is using UDP!')
                    u = pkt.get_protocol(udp.udp)
                    match = ofp_parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP, ipv4_src=ip4.src, ipv4_dst=ip4.dst, ip_proto=protocol, udp_src=u.src_port, udp_dst=u.dst_port)
                else:
                    self.logger.info("Don't know how to handle protocol: " + str(protocol) + "; Won't add any rules")
                    match = None
                # self.logger.info(pkt.get_protocol(tcp.tcp))
                # if pkt.get_protocol(tcp.tcp):
                #     self.logger.info('TCP!')
                
                if msg.buffer_id == ofp.OFP_NO_BUFFER:
                    self.logger.info("This message doesn't reference a buffer")
                else:
                    self.logger.info('Buffer ID: %s', msg.buffer_id)
                
                if match is not None:
                    
                    self.logger.info("Match was not none; Proceeding to possibly add flow")

                    # set priority for tcp and udp
                    if t:
                        priority = 1
                    elif u:
                        priority = 2
                    else:
                        priority = 3
                    
                    if msg.buffer_id != ofp.OFP_NO_BUFFER:
                        
                        self.logger.info("Message buffer ID was not \"no buffer\"; Proceeding to add a flow")

                        self.send_flow_mod(
                            dp, match, actions,
                            new_priority=priority,
                            new_buffer_id=msg.buffer_id
                        )
                        
                    else:
                        self.logger.info(
                            "Message buffer ID was \"no buffer\"; Proceeding to add flow without specifying buffer"
                        )
                        self.send_flow_mod(
                            dp, match, actions,
                            new_priority=priority
                        )
            
            # for p in pkt:
            #     # print(p.protocol_name, p)
            #     self.logger.info(p)
            
            # Switch didn't already know this port
        else:
            # self.logger.info("Switch didn't already know destination " + str(dst) + " mapped to port " + str(out_port))
            # self.logger.info("Mac-to-Port dictionary looks like: " + str(self.mac_to_port))
            pass
        
        # out = ofp_parser.OFPPacketOut(
        #     datapath=dp,
        #     buffer_id=ofp.OFP_NO_BUFFER,
        #     in_port=in_port, actions=actions,
        #     data=msg.data
        # )
        # dp.send_msg(out)

        data = None
        if msg.buffer_id == ofp.OFP_NO_BUFFER:
            data = msg.data

        out = ofp_parser.OFPPacketOut(
            datapath=dp, buffer_id=msg.buffer_id,
            in_port=in_port, actions=actions, data=data
        )
        dp.send_msg(out)
        
        self.logger.info("End packet_in_handler")
