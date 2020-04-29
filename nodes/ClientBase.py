

from nodes.HostBase import HostBase


class ClientBase(HostBase):
	
	def __init__(self, net, topology, host):
		
		super(ClientBase, self).__init__(net, topology, host)
