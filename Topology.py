

from Logger import Logger

import graphviz

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.link import TCLink
from mininet.node import OVSSwitch


import os
import subprocess


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
	
	__mac_address_base = "00:00:00:00:00:"  # Obviously like 255 host macs with this scheme
	__mac_address_counter = 1
	
	__ip_address_base = "10.0.0."
	__ip_counter = 1
	
	__BANDWIDTH_LIMIT_SERVERS_MBPS = 1000
	__BANDWIDTH_LIMIT_SERVERS_DELAY = "0.5ms"
	
	__BANDWIDTH_LIMIT_CLIENTS_MBPS = 100
	__BANDWIDTH_LIMIT_CLIENTS_DELAY = "1ms"
	
	def __init__(self, logger):
		
		self.__logger = logger
		# type: Logger
		
		super(Topology, self).__init__()
	
	# Should be run after build
	def set_net(self, net: Mininet):
		
		self.__net = net
		
		self.consume_instances()
	
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
		"""
		self.addLink(
			self.__main_switch_name,
			self.__file_server_name,
			intfName1="switch-fs",
			cls=TCLink, bw=self.__BANDWIDTH_LIMIT_SERVERS_MBPS, delay=self.__BANDWIDTH_LIMIT_SERVERS_DELAY
		)
		"""
		self.add_link_to_main_switch(
			node_name=self.__file_server_name,
			interface_name="switch-fs",
			preferred_mbps=self.__BANDWIDTH_LIMIT_SERVERS_MBPS,
			preferred_delay=self.__BANDWIDTH_LIMIT_SERVERS_DELAY
		)
		
		# Create video server host
		log.info("Creating video server host")
		self.add_host_with_addresses(self.__video_server_name)
		"""
		self.addLink(
			self.__main_switch_name,
			self.__video_server_name,
			intfName1="switch-vs",
			cls=TCLink, bw=self.__BANDWIDTH_LIMIT_SERVERS_MBPS, delay=self.__BANDWIDTH_LIMIT_SERVERS_DELAY
		)
		"""
		self.add_link_to_main_switch(
			node_name=self.__video_server_name,
			interface_name="switch-vs",
			preferred_mbps=self.__BANDWIDTH_LIMIT_SERVERS_MBPS,
			preferred_delay=self.__BANDWIDTH_LIMIT_SERVERS_DELAY
		)
		
		# Create our tattle tail host
		log.info("Creating tattle tail host")
		self.add_host_with_addresses(self.__tattle_tail_name)
		"""
		self.addLink(
			self.__main_switch_name, self.__tattle_tail_name,
			intfName1="switch-tt",
			cls=TCLink, bw=self.__BANDWIDTH_LIMIT_CLIENTS_MBPS, delay=self.__BANDWIDTH_LIMIT_CLIENTS_DELAY
		)
		"""
		self.add_link_to_main_switch(
			node_name=self.__tattle_tail_name,
			interface_name="switch-tt",
			preferred_mbps=self.__BANDWIDTH_LIMIT_CLIENTS_MBPS,
			preferred_delay=self.__BANDWIDTH_LIMIT_CLIENTS_DELAY
		)
		
		# Create file clients
		log.info("Creating file clients")
		for i in range(self.__file_client_hosts_count):
			client_name = self.__file_client_name_prefix + str(i + 1)
			log.info("Creating file client: " + client_name)
			self.add_host_with_addresses(client_name)
			"""
			self.addLink(
				self.__main_switch_name,
				client_name,
				intfName1="switch-" + client_name,
				cls=TCLink, bw=self.__BANDWIDTH_LIMIT_CLIENTS_MBPS, delay=self.__BANDWIDTH_LIMIT_CLIENTS_DELAY
			)
			"""
			self.add_link_to_main_switch(
				node_name=client_name,
				interface_name="switch-" + client_name,
				preferred_mbps=self.__BANDWIDTH_LIMIT_CLIENTS_MBPS,
				preferred_delay=self.__BANDWIDTH_LIMIT_CLIENTS_DELAY
			)
			self.__file_client_names.append(client_name)
		
		# Create video clients
		log.info("Creating video clients")
		for i in range(self.__video_client_hosts_count):
			client_name = self.__video_client_name_prefix + str(i + 1)
			log.info("Creating video client: " + client_name)
			self.add_host_with_addresses(client_name)
			"""
			self.addLink(
				self.__main_switch_name,
				client_name,
				intfName1="switch-" + client_name,
				cls=TCLink, bw=self.__BANDWIDTH_LIMIT_CLIENTS_MBPS, delay=self.__BANDWIDTH_LIMIT_CLIENTS_DELAY
			)
			"""
			self.add_link_to_main_switch(
				node_name=client_name,
				interface_name="switch-" + client_name,
				preferred_mbps=self.__BANDWIDTH_LIMIT_CLIENTS_MBPS,
				preferred_delay=self.__BANDWIDTH_LIMIT_CLIENTS_DELAY
			)
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
		
		# Works for up to 255 hosts
		
		suffix_int = self.__mac_address_counter
		self.__mac_address_counter += 1
		
		suffix = hex(suffix_int)[2:]
		if len(suffix) == 1:
			suffix = "0" + suffix
		
		mac = self.__mac_address_base
		mac += suffix
		
		return mac
	
	def add_switch_with_addresses(self, name):
		
		mac = self.get_next_mac_address()
		ip = self.get_next_ip()
		
		self.__logger.get().info("Adding switch with " + ip + "; " + mac)
		
		return self.addSwitch(
			name,
			mac=mac,
			ip=ip,
			cls=OVSSwitch
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
	
	def add_link_to_main_switch(self, node_name, interface_name=None, preferred_mbps=None, preferred_delay=None):
		
		# Yes disable because some forum said this might interfere with vswitch queue stuff
		disable_limiting = True
		
		if disable_limiting is False and (preferred_mbps is not None or preferred_delay is not None):
			
			self.addLink(
				self.__main_switch_name,
				node_name,
				intfName1=interface_name,
				cls=TCLink,
				bw=self.__BANDWIDTH_LIMIT_CLIENTS_MBPS,
				delay=self.__BANDWIDTH_LIMIT_CLIENTS_DELAY
			)
			
		else:
			
			self.addLink(
				self.__main_switch_name,
				node_name,
				intfName1=interface_name
			)
	
	def get_file_server_instance(self):
		
		return self.__file_server_instance
	
	def get_video_server_instance(self):
		
		return self.__video_server_instance
	
	def get_tattle_tail_instance(self):
		
		return self.__tattle_tail_instance
	
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
			self.__file_client_instances[name] = self.__net.nameToNode[name]
		
		# Grab video client instances
		self.__video_client_instances = dict()
		for name in self.__video_client_names:
			self.__video_client_instances[name] = self.__net.nameToNode[name]
		
		# Grab tattle tail
		self.__tattle_tail_instance = self.__net.nameToNode[self.__tattle_tail_name]
		
		#
		log.info("Done consuming instances")
	
	def get_file_client_instances(self):
		
		return self.__file_client_instances
	
	def get_video_client_instances(self):
	
		return self.__video_client_instances
	
	# Heavy inspiration: http://docs.openvswitch.org/en/latest/topics/dpdk/qos/
	# Also: https://github.com/mininet/mininet/pull/132
	def create_qos_queues(self):
		
		log = self.__logger.get()
		
		result = self.__main_switch_instance.setup()
		log.info("Hey: " + str(self.__main_switch_instance) + "; " + str(result))
		
		# ovs_path = "/usr/bin/ovs-vsctl"
		ovs_path = "ovs-vsctl"
		
		#
		args = list([
			ovs_path,
			"--", "set", "port", "switch-fs", "qos=@newqos",
			"--", "set", "port", "switch-vs", "qos=@newqos",
			"--", "--id=@newqos", "create", "qos", "type=trtcm-policer", "queues=0=@q0,1=@q1",
			# "--", "--id=@q0", "create", "queue", "other-config:cir=41600000", "other-config:eir=0", "other-config:priority=0",
			# "--", "--id=@q1", "create", "queue", "other-config:cir=0", "other-config:eir=41600000", "other-config:priority=1"
			"--", "--id=@q0", "create", "queue", "other-config:priority=0", "other-config:maxrate=1000000",
			"--", "--id=@q1", "create", "queue", "other-config:priority=1", "other-config:maxrate=1000000"
		])
		# Try to setup the QoS setup and its queues
		p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		result = p.communicate()
		# qos_id = result.splitlines()[0]
		log.info("Trying to get ovswitch stuff working ... " + str(result))
		# log.info("QoS ID is apparently: " + qos_id)
		
		#
		log.info("Switch interface names: " + str(self.__main_switch_instance.intfNames()))
		for intf in self.__main_switch_instance.intfList():
			log.info("Uhm interface: " + str(intf) + "; " + intf.name)
		
		"""
		result = self.__main_switch_instance.cmd([
			ovs_path,
			"set Port %s qos=%s" % ("switch-vs", qos_id)
		])
		log.info("Trying to hard set ports to different queues ... " + str(result))
		#
		result = self.__main_switch_instance.cmd([
			ovs_path,
			"set Port %s qos=%s" % ("'switch-fs'", "q1")
		])
		log.info("Trying to hard set ports to different queues ... " + str(result))
		"""
		
		result = self.__main_switch_instance.cmd([ovs_path, "list-br"])
		log.info("Executed erm ... " + str(result))
	
	def create_qos_queues_on_switch(self):
		
		log = self.__logger.get()
		
		self.__main_switch_instance.setup()
		
		# ovs_path = "/usr/bin/ovs-vsctl"
		ovs_path = "ovs-vsctl"
		
		# qos_type = "trtcm-policer"
		qos_type = "linux-htb"
		
		# Try to setup the QoS setup and its queues
		# "--", "--id=@q0", "create", "queue", "other-config:priority=0", "other-config:max-rate=100000000",
		args = list([
			ovs_path,
			"--", "--id=@newqos", "create", "qos", "type=" + qos_type, "queues=0=@q0,1=@q1",
			"--", "--id=@q0", "create", "queue", "other-config:priority=0", "other-config:max-rate=100000000",
			"--", "--id=@q1", "create", "queue", "other-config:priority=1", "other-config:max-rate=100000000"
		])
		for intf_name in self.__main_switch_instance.intfNames():
			if intf_name != "lo":
				args += ["--", "set", "Port", intf_name, "qos=@newqos"]
		
		log.info("Trying to initialize Open VSwitch qos stuffs: \n%s", args)
		result = self.__main_switch_instance.cmd(args)
		qos_id = result.splitlines()[0]
		log.info("Result of OpenVSwitch init command: %s", str(result))
		log.info("QoS ID is apparently: " + qos_id)
		
		#
		log.info("Switch interface names: " + str(self.__main_switch_instance.intfNames()))
		
		result = self.__main_switch_instance.cmd([ovs_path, "-t", "ovs-vswitchd", "show"])
		log.info("Showing OpenvSwitch information: " + str(result))
		
		result = self.__main_switch_instance.cmd([ovs_path, "list-br"])
		log.info("Showing OpenvSwitch information: " + str(result))
