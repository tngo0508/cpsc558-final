

from nodes.HostBase import HostBase


class TattleTail(HostBase):
	
	def __init__(self, net, topology, host):
		
		super(TattleTail, self).__init__(net, topology, host)
	
	def __str__(self):
		
		s = ""
		
		s += "TattleTail Instance"
		# s += "; MAC = " + self.__host.MAC()
		# s += "; IP = " + self.__host.IP()
		
		return s
