

from Logger import Logger
from Topology import Topology


from mininet.node import Controller as MininetController


class Controller(MininetController):
	
	__name = "My Custom Controller"
	
	def __init__(self, logger, topology):
		
		# type: (Logger, Topology) -> None
		
		MininetController.__init__(self, self.__name)
		
		self.__logger = logger
		self.__topology = topology
