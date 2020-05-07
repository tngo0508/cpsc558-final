

from nodes.ServerBase import ServerBase

import socket


class VideoServer(ServerBase):
	
	__listen_port = 8013
	
	def __init__(self, run_name, name):
		
		super(VideoServer, self).__init__(
			run_name,
			name,
			socket.SOCK_DGRAM, None, self.__listen_port
		)
	
	def run(self):
		
		self.start_listener_loop()
	
	def start_listener_loop(self):
		
		log = self.logger().get()
		
		log.info("Begin start_listener_loop")
		sock = self.socket()
		
		# Set a timeout on our socket because we were getting stucked
		sock.settimeout(0.01)
		
		reply_data = "Z" * 1024
		reply_data = reply_data.encode()
		
		log.info("About to enter listener loop")
		while True:
			
			# log.info("Begin trying to receive data from socket: " + str(sock))
			try:
				data, sender = sock.recvfrom(1024)
			except socket.timeout:
				log.warning("Socket timeout while trying to receive from client")
				continue
			log.info("Received " + str(len(data)) + " bytes from " + str(sender) + "; Sending data")
			
			# Send back some megabytes
			for i in range(1024):
				
				try:
					sock.sendto(reply_data, sender)
				except socket.timeout:
					log.warning("Socket timed out; This loop won't count")
					i -= 1
			log.info("Done sending data to " + str(sender))
