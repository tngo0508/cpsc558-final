

from nodes.ClientBase import ClientBase


class FileClient(ClientBase):
	
	def __init__(self, net, topology, host):
		
		super(FileClient, self).__init__(net, topology, host)
