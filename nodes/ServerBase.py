

from Logger import Logger

import socket
import subprocess


class ServerBase:
	
	__default_bind_address = ""
	
	__socket_type = None
	__bind_address = None
	__listen_port = None
	
	__socket = None
	
	def __init__(self, name, socket_type, bind_address, listen_port):
		
		if bind_address is None:
			bind_address = self.__default_bind_address
		
		self.__socket_type = socket_type
		self.__bind_address = bind_address
		self.__listen_port = listen_port
		
		my_ip = subprocess.check_output(["hostname", "-I"]).decode().strip()
		self.__logger = Logger(
			"Server " + my_ip + "::" + str(listen_port)
			+ "(" + self.socket_type_to_string() + ")",
			name
		)
		
		self.start_listening()
		
	def __del__(self):
		
		self.stop_listening()
	
	def socket_type_to_string(self):
	
		if self.__socket_type == socket.SOCK_STREAM:
			return "TCP"
		elif self.__socket_type == socket.SOCK_DGRAM:
			return "UDP"
		
		return "???"
	
	def start_listening(self):
		
		self.__logger.get().info("Begin listening")
		
		self.stop_listening()
		
		self.__logger.get().info("Creating socket")
		self.__socket = socket.socket(socket.AF_INET, self.__socket_type)
		self.__logger.get().info("Binding socket to listen address")
		self.__socket.bind((self.__bind_address, self.__listen_port))
		
	def stop_listening(self):
		
		self.__logger.get().info("Making sure we're not listening")
		
		if self.__socket is not None:
			
			self.__logger.get().info("We were listening; Shutting down")
			
			self.__socket.close()
			self.__socket = None
	
	def socket(self):
		
		return self.__socket
	
	def logger(self):
		
		return self.__logger
