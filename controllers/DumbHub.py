

from Logger import Logger

import ryu
from ryu.base import app_manager
from ryu.ofproto import ofproto_v1_0
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller import ofp_event
from ryu.controller.handler import set_ev_cls
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet

from mininet.node import Ryu


class DumbHub(app_manager.RyuApp):
	
	OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]
	
	def __init__(self, *args, **kwargs):
		
		self.__logger = Logger("DumbHub")
		
		super(DumbHub, self).__init__(*args, **kwargs)
	
	# This method will receive packets from switches
	@set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
	def packet_in_handler(self, ev):
		
		log = self.__logger.get()
		
		log.info("Received packet!")
		
		msg = ev.msg
		datapath = msg.datapath
		ofproto = datapath.ofproto
		
		pkt = packet.Packet(msg.data)
		eth = pkt.get_protocol(ethernet.ethernet)
		
		# log.info("Got message: " + str(msg))
		# log.info("Got datapath: " + str(datapath))
		# log.info("Got ofproto: " + str(ofproto))
		# log.info("Got a packet: " + str(pkt))
		# log.info("Got an ethernet protocol thing: " + str(eth))
