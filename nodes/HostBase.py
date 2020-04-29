

from Logger import Logger

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import Host as mininet_host


class HostBase(mininet_host):
	
	__topology = None
	__host = None
	
	def __init__(self, run_name, net: Mininet, topology: Topo, host: mininet_host):
		
		super(HostBase, self).__init__(host.name)
		
		self.__logger = Logger(
			group=run_name,
			log_name=host.name,
			label="Host: " + host.name
		)
		
		self.__net = net
		self.__topology = topology
		self.__host = host
		self.__name = host.name
		
		self.__logger.get().info("Instantiated")
	
	def __str__(self):
		
		s = ""
		
		s += "HostBase Instance"
		s += "; MAC = " + self.__host.MAC()
		s += "; IP = " + self.__host.IP()
		
		return s
	
	def host(self):
		
		return self.__host
	
	def name(self):
		
		return self.__name
