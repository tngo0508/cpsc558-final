

from nodes.ServerBase import ServerBase

import socket


class FileServer(ServerBase):
	
	__listen_port = 8013
	
	def __init__(self, mininet, topology, host):
		
		super(FileServer, self).__init__(
			mininet, topology, host,
			socket.SOCK_STREAM, None, self.__listen_port
		)
