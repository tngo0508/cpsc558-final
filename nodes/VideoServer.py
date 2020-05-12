

from nodes.ServerBase import ServerBase

import math
import socket
import threading


class VideoServer(ServerBase):
	
	__listen_port = 8013
	__socket_timeout_seconds = 1
	
	# https://stackoverflow.com/questions/53530631/failed-to-send-bytes-over-sockets-message-too-long
	__udp_max_bytes = 65507
	
	__megabytes_to_send = 100
	
	__handled_clients = list()
	
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
		sock.settimeout(self.__socket_timeout_seconds)
		
		log.info("About to enter listener loop")
		while True:
			
			# log.info("Begin trying to receive data from socket: " + str(sock))
			try:
				data, client = sock.recvfrom(1024)
			except socket.timeout:
				log.warning("Socket timeout while trying to receive from client")
				continue
			log.info("Received " + str(len(data)) + " bytes from " + str(client) + "; Sending data")
			
			#
			if client in self.__handled_clients:
				log.info("Ignoring remnant client initialization request from: " + str(client))
				continue
			
			# Send back some megabytes
			thread = threading.Thread(target=self.send_data_to_client, kwargs={"sock": sock, "client": client})
			thread.start()
			
			# Remember this client so we don't send again
			self.__handled_clients.append(client)
	
	def send_data_to_client(self, sock, client):
		
		log = self.logger().get()
		
		# reply_data = "Z" * self.__udp_max_bytes
		reply_data = "Z" * 1024
		reply_data = reply_data.encode()
		
		bytes_remaining = math.floor(
			self.__megabytes_to_send * 1024 * 1024
		)
		
		while bytes_remaining > 0:
			
			try:
				bytes_sent = sock.sendto(reply_data, client)
				bytes_remaining -= bytes_sent
			except socket.timeout:
				log.warning("Socket timed out while trying to send")
		
		log.info("Done sending data to " + str(client))
