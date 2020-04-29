

from Logger import Logger
from nodes.FileServer import FileServer
from nodes.FileClient import FileClient
from nodes.VideoServer import VideoServer
from nodes.VideoClient import VideoClient
from nodes.TattleTail import TattleTail

import graphviz

from mininet.net import Mininet
from mininet.topo import Topo

import os


class Topology(Topo):
	
	"""
	Topology initializer for CPSC 558 Final Project
	"""
	
	__net = None
	
	__logger = None
	
	__main_switch_name = "S1"
	__main_switch_ip = None
	__main_switch_instance = None
	
	__file_server_name = "FS"
	__file_server_instance = None
	
	__video_server_name = "VS"
	__video_server_instance = None
	
	__tattle_tail_name = "TT"
	__tattle_tail_instance = None
	
	__file_client_name_prefix = "FC"
	__file_client_hosts_count = 2
	__file_client_names = None
	__file_client_instances = None
	
	__video_client_name_prefix = "VC"
	__video_client_hosts_count = 2
	__video_client_names = None
	__video_client_instances = None
	
	__mac_address_base = "00:00:00:00:00:0"  # Obviously only like 15 hosts mac with this scheme
	__mac_address_counter = 1
	
	__ip_address_base = "10.0.0."
	__ip_counter = 1
	
	def __init__(self, logger):
		
		self.__logger = logger
		# type: Logger
		
		super(Topology, self).__init__()
		
	def set_net(self, net: Mininet):
	
		self.__net = net
	
	def build(self):
		
		log = self.__logger.get()
		
		self.reset_mac_address_counter()
		self.reset_ip_counter()
		
		#
		log.info("Clearing topology")
		self.__file_client_names = list()
		self.__video_client_names = list()
		
		# Create our main switch
		log.info("Creating main switch")
		self.add_switch_with_addresses(self.__main_switch_name)
		
		# Create file server host
		log.info("Creating file server host")
		self.add_host_with_addresses(self.__file_server_name)
		self.addLink(self.__main_switch_name, self.__file_server_name)
		
		# Create video server host
		log.info("Creating video server host")
		self.add_host_with_addresses(self.__video_server_name)
		self.addLink(self.__main_switch_name, self.__video_server_name)
		
		# Create our tattle tail host
		log.info("Creating tattle tail host")
		self.add_host_with_addresses(self.__tattle_tail_name)
		self.addLink(self.__main_switch_name, self.__tattle_tail_name)
		
		# Create file clients
		log.info("Creating file clients")
		for i in range(self.__file_client_hosts_count):
			client_name = self.__file_client_name_prefix + str(i + 1)
			log.info("Creating file client: " + client_name)
			self.add_host_with_addresses(client_name)
			self.addLink(self.__main_switch_name, client_name)
			self.__file_client_names.append(client_name)
		
		# Create video clients
		log.info("Creating video clients")
		for i in range(self.__video_client_hosts_count):
			client_name = self.__video_client_name_prefix + str(i + 1)
			log.info("Creating video client: " + client_name)
			self.add_host_with_addresses(client_name)
			self.addLink(self.__main_switch_name, client_name)
			self.__video_client_names.append(client_name)
		
		#
		log.info("Finished building topology")
	
	def reset_ip_counter(self):
		
		self.__ip_counter = 1
	
	def get_next_ip(self):
		
		ip = self.__ip_address_base + str(self.__ip_counter)
		self.__ip_counter += 1
		
		return ip
	
	def reset_mac_address_counter(self):
		
		self.__mac_address_counter = 0
	
	def get_next_mac_address(self):
		
		mac = self.__mac_address_base
		mac += str(self.__mac_address_counter)
		
		self.__mac_address_counter += 1
		
		return mac
	
	def add_switch_with_addresses(self, name):
		
		mac = self.get_next_mac_address()
		ip = self.get_next_ip()
		
		self.__logger.get().info("Adding switch with " + ip + "; " + mac)
		
		return self.addSwitch(
			name,
			mac=mac,
			ip=ip
		)
	
	def add_host_with_addresses(self, name):
		
		mac = self.get_next_mac_address()
		ip = self.get_next_ip()
		
		self.__logger.get().info("Adding host with " + ip + "; " + mac)
		
		host = self.addHost(
			name,
			mac=mac,
			ip=ip
		)
		
		return host
	
	def get_file_server_instance(self):
		
		return self.__file_server_instance
	
	def get_video_server_instance(self):
		
		return self.__video_server_instance
	
	def render_dotgraph(self, view=False):
		
		dot = self.generate_dotgraph()
		
		file_path = os.path.join(
			os.path.dirname(__file__),
			"render",
			"topology"
		)
		
		dot.render(file_path, format="png", view=view)
	
	def generate_dotgraph(self):
		
		s = ""
		
		for switch_name in self.switches():
			
			s += "\n\t" + switch_name
			s += "["
			s += "label=\"" + self.get_node_label(switch_name) + "\""
			s += "];"
		
		for host_name in self.hosts():
			
			s += "\n\t" + host_name
			s += "["
			s += "label=\"" + self.get_node_label(host_name) + "\""
			s += "];"
		
		for link in self.links():
			
			first, second = link
			
			s += "\n\t" + first + " -- " + second
		
		# Server ranks
		h = [self.__video_server_name]
		h.extend([self.__file_server_name])
		s += "\n\t{rank=source;" + ";".join(h) + "};"
		
		# Client rank
		hosts_names = []
		for h in self.__video_client_names:
			hosts_names.append(h)
		for h in self.__file_client_names:
			hosts_names.append(h)
		s += "\n\t{rank=same;" + ";".join(hosts_names) + "};"
		
		# Tattle tail rank
		s += "\n\t{rank=sink;" + self.__tattle_tail_name + "};"
		
		dot = graphviz.Graph(name="CPSC 558 Final Project", body=s.split("\n"))
		
		return dot
	
	def get_node_label(self, node_name):
		
		if node_name == self.__video_server_name:
			under = "video server"
		elif node_name == self.__file_server_name:
			under = "file server"
		elif node_name in self.__video_client_names:
			under = "video client"
		elif node_name in self.__file_client_names:
			under = "file client"
		elif node_name == self.__tattle_tail_name:
			under = "tattle tail"
		elif self.isSwitch(node_name):
			under = "switch"
		else:
			under = "host"
		
		label = node_name + "\\n(" + under + ")"
		
		if self.__net:
			node = self.__net.getNodeByName(node_name)
			label += "\n(" + node.IP() + ")"
		
		return label
	
	def consume_instances(self):
		
		log = self.__logger.get()
		log.info("Consuming instances from Mininet to Topology class")
		
		# Grab the switch
		self.__main_switch_instance = self.__net.nameToNode[self.__main_switch_name]
		
		# Grab the servers
		self.__video_server_instance = self.__net.nameToNode[self.__video_server_name]
		self.__file_server_instance = self.__net.nameToNode[self.__file_server_name]
		
		# Grab file client instances
		self.__file_client_instances = dict()
		for name in self.__file_client_names:
			self.__file_client_instances[name] = FileClient(self.__net, self, self.__net.nameToNode[name])
		
		# Grab video client instances
		self.__video_client_instances = dict()
		for name in self.__video_client_names:
			self.__video_client_instances[name] = self.__net.nameToNode[name]
		
		# Grab tattle tail
		self.__tattle_tail_instance = TattleTail(self.__net, self, self.__net.nameToNode[self.__tattle_tail_name])
		
		#
		log.info("Done consuming instances")
	
	def get_file_client_instances(self):
		
		return self.__file_client_instances
	
	def get_video_client_instances(self):
	
		return self.__video_client_instances
