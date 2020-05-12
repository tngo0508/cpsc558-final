"""

We wrote this code, but relied heavily on the following sources for inspiration:

https://osrg.github.io/ryu-book/en/html/switching_hub.html#adding-table-miss-flow-entry
https://ryu.readthedocs.io/en/latest/writing_ryu_app.html
https://github.com/osrg/ryu/blob/master/ryu/app/simple_switch.py
https://ryu.readthedocs.io/en/latest/ofproto_v1_3_ref.html#modify-state-messages
https://ryu.readthedocs.io/en/latest/ofproto_v1_3_ref.html
https://github.com/knetsolutions/learn-sdn-with-ryu/blob/master/ryu-exercises/ex3_L4Match_switch.py

Please keep the above admission fully in mind if you see any similarities :)

"""

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import HANDSHAKE_DISPATCHER, MAIN_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3, ofproto_v1_0, ofproto_v1_2, ofproto_v1_4, ofproto_v1_5
from ryu.lib.packet import packet, in_proto, icmp, tcp, udp, ipv4, ipv6
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
# from ryu.lib.mac import haddr_to_bin
import collections


class QSwitch(app_manager.RyuApp):
	
	OFP_VERSIONS = [
		ofproto_v1_3.OFP_VERSION,
		ofproto_v1_4.OFP_VERSION,
		ofproto_v1_0.OFP_VERSION,
		ofproto_v1_2.OFP_VERSION,
		ofproto_v1_5.OFP_VERSION
	]
	
	__flow_add_counter = 0
	
	def __init__(self, *args, **kwargs):
		
		super(QSwitch, self).__init__(*args, **kwargs)
		
		self.logger.info(type(self).__name__ + " is initializing")
		
		self.mac_to_port = collections.defaultdict()  # used to learn MAC addr
		
		self.logger.info(type(self).__name__ + " has initialized")
	
	def __del__(self):
	
		self.logger.info("Begin __del__")
		
		self.logger.info("Tried to add a flow " + str(self.__flow_add_counter) + " times")
		
		self.logger.info("End __del__")
	
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
	
	def is_packet_ipv4(self, p_in):
		
		d = p_in.get_protocol(ipv4.ipv4)
		if d:
			return True
		
		return False
	
	def is_packet_ipv6(self, p_in):
		
		d = p_in.get_protocol(ipv6.ipv6)
		if d:
			return True
		
		return False
	
	def get_packet_ip_proto_version(self, p):
	
		if self.is_packet_ipv4(p):
			return 4
		elif self.is_packet_ipv6(p):
			return 6
		
		return None
	
	def is_packet_tcp(self, p_in):
		
		t = p_in.get_protocol(tcp.tcp)
		if t:
			return True
		return False
	
	def is_packet_udp(self, p_in):
		
		u = p_in.get_protocol(udp.udp)
		if u:
			return True
		return False
	
	def is_packet_icmp(self, p_in):
		
		i = p_in.get_protocol(icmp.icmp)
		if i:
			return True
		return False
	
	# function template at https://ryu.readthedocs.io/en/latest/ofproto_v1_3_ref.html#modify-state-messages
	def send_flow_mod(self, datapath, match, actions, new_priority=0):
		
		self.logger.info("\nBegin send_flow_mod(); " + str(self.__flow_add_counter) + " times")
		self.logger.info("Match: " + str(match))
		self.logger.info("Actions: " + str(actions))
		
		self.__flow_add_counter += 1
		
		ofp = datapath.ofproto
		ofp_parser = datapath.ofproto_parser
		
		cookie = cookie_mask = 0
		table_id = 0
		idle_timeout = hard_timeout = 0
		priority = new_priority
		buffer_id = ofp.OFP_NO_BUFFER
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
			idle_timeout=idle_timeout, hard_timeout=hard_timeout
		)
		
		# self.logger.info("Sending message to our datapath: " + str(req))
		datapath.send_msg(req)
		
		# self.logger.info("End send_flow_mod()")
	
	@set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
	def simple_switch_features_handler(self, ev):
		
		self.logger.info("Begin simple_switch_features_handler")
		
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
		# self.logger.info("Got datapath: " + str(dp.id))
		
		ofp = dp.ofproto  # the protocol that Openflow version in use
		ofp_parser = dp.ofproto_parser
		
		pkt = packet.Packet(msg.data)
		eth = pkt.get_protocol(ethernet.ethernet)
		# self.logger.info("Packet: %s", pkt)
		
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
		
		# Start with just an action that specifies which port(s) to send out on
		actions = [
			ofp_parser.OFPActionOutput(out_port)
		]
		
		# Let's add a flow if we're not flooding
		if out_port != ofp.OFPP_FLOOD:
			
			self.logger.info("\nWe are not flooding; Will try to save a new flow")
			
			flow_entry_priority = 1
			
			# Start some match arguments
			# Always match on ethertype so we don't stomp on our IP flows
			match_extra_kwargs = dict({
				"eth_type": eth.ethertype
			})
			
			# Try to determine if this is a TCP or UDP flow (or nonw)
			is_tcp = self.is_packet_tcp(pkt)
			is_udp = self.is_packet_udp(pkt)
			is_icmp = self.is_packet_icmp(pkt)
			
			#
			self.logger.info(
				"ethertype %s; is_tcp %s; is_udp %s; is_icmp %s", eth.ethertype, is_tcp, is_udp, is_icmp
			)
			
			# Enhance the match and use the queue if we're a TCP or UDP flow
			if eth.ethertype == ether_types.ETH_TYPE_IP and (is_tcp or is_udp or is_icmp):
				
				self.logger.info("We appear to have a TCP or UDP flow")
				
				queue_number = 0
				
				ip_version = self.get_packet_ip_proto_version(pkt)
				if is_tcp:
					ip_proto = in_proto.IPPROTO_TCP
				elif is_udp:
					ip_proto = in_proto.IPPROTO_UDP
				else:
					ip_proto = in_proto.IPPROTO_ICMP
				
				match_extra_kwargs["ip_proto"] = ip_proto
				
				if is_tcp:
					# self.logger.info("Gonna match on a TCP port")
					t = pkt.get_protocol(tcp.tcp)
					match_extra_kwargs["tcp_dst"] = t.dst_port
				elif is_udp:
					# self.logger.info("Gonna match on a UDP port")
					u = pkt.get_protocol(udp.udp)
					match_extra_kwargs["udp_dst"] = u.dst_port
					queue_number = 1
				else:
					
					ic = pkt.get_protocol(icmp.icmp)
					
					if ip_version == 6:
						match_extra_kwargs["icmpv6_type"] = ic.type
					else:
						match_extra_kwargs["icmpv4_type"] = ic.type
				
				# Add an action that sends this flow to a queue
				actions.insert(0, ofp_parser.OFPActionSetQueue(queue_number))
			
			# Start the match object
			# self.logger.info("Setting match kwargs: " + str(match_extra_kwargs))
			match = ofp_parser.OFPMatch(
				eth_src=src_mac,
				eth_dst=dst_mac,
				in_port=in_port,
				**match_extra_kwargs
			)
			self.logger.info("Match is now: " + str(match))
			
			# Send out the flow, woot
			self.send_flow_mod(dp, match, actions, flow_entry_priority)
		
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
