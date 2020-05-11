

from Logger import Logger
from Benchmarker import Benchmarker


import select
import socket
import subprocess
import threading
import time


class VideoClient:
	
	# Sorry not sorry
	__default_server_port = 8013
	
	#
	__server_host = None
	__server_port = None
	
	#
	__socket = None
	__listener_thread = None
	
	__beg_string = "Gimme!".encode()
	
	def __init__(self, run_name, name, server_host=None, server_port=None):
		
		my_ip = subprocess.check_output(["hostname", "-I"]).decode().strip()
		
		if name is None:
			name = my_ip
		
		self.__logger = Logger(
			group=run_name,
			log_name=name,
			label="VideoClient"
		)
		
		if server_host is None:
			raise Exception("Need to specify server host")
		self.__server_host = server_host
		
		if server_port is None:
			server_port = self.__default_server_port
		self.__server_port = server_port
		
		self.__benchmarker = Benchmarker(name)
		
		# self.__logger.set_verbose(True)
		
	def __del__(self):
		
		if threading.current_thread == threading.main_thread() and self.__listener_thread:
			
			self.__listener_thread.join()
			self.__listener_thread = None
	
	def run(self):
		
		log = self.__logger.get()
		
		log.info("Running ...")
		
		self.init_socket()
		self.receive_from_server()
		
		log.info("Finished running")
		
	def init_socket(self):
		
		self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		# self.__socket.bind((self.__server_host, self.__server_port))
	
	def init_data_receiver(self):
		
		self.__listener_thread = threading.Thread(target=self.data_receiver)
		self.__listener_thread.start()
	
	def data_receiver(self):
		
		log = self.__logger.get()
		
		while self.__benchmarker.is_running():
			
			log.debug("Data receiver iteration")
			
			if self.socket_has_data():
				
				# log.info("Receiving ... ")
				
				received, sender = self.__socket.recvfrom(1048576)
				self.__benchmarker.increased_bytes_received(len(received))
				
				log.info(
					"Received " + str(len(received)) + " bytes from" + str(sender)
					+ "; Total = " + str(self.__benchmarker.get_bytes_received())
				)
				
			else:
				time.sleep(.0001)
	
	def kickstart_server(self):
		
		log = self.__logger.get()
		
		log.info("Begin kickstart_server")
		
		# Send 1024 of pleas for data
		for i in range(1024):
			
			log.info("Asking server to start sending data")
			
			self.ask_server_for_data()
		
		log.info("End kickstart_server")
	
	def receive_from_server(self):
		
		log = self.__logger.get()
		
		log.info("Begin wait_for_server_finished")
		
		self.kickstart_server()
		
		self.__benchmarker.start()
		self.init_data_receiver()  # Must happen after benchmark starts
		no_data_count = 0
		while no_data_count < 15:
			
			# log.info("Iteration of loop: wait_for_server_finished")
			
			if self.socket_has_data():
				
				no_data_count = 0
				log.info("Got some data from server; Total %s megabytes", self.__benchmarker.get_megabytes_received())
				
			else:
				
				no_data_count += 1
				log.info("wait_for_server_finished() - No incoming data; Count is: " + str(no_data_count))
			
			time.sleep(1)
		
		self.__benchmarker.stop()
		self.__benchmarker.adjust_end_time(no_data_count)  # For the 10 second timeout
		log.info(self.__benchmarker)
		
		log.info("End leech loops")
	
	def ask_server_for_data(self):
		
		log = self.__logger.get()
		
		log.info("Asking server for data: " + str(self.__server_host) + "::" + str(self.__server_port))
		self.__socket.sendto(self.__beg_string, (self.__server_host, self.__server_port))
		# log.info("Done asking server for data")
		
	def socket_has_data(self):
		
		# log = self.__logger.get()
		
		# log.info("Checking socket for data")
		if self.__socket:
			read_sockets, write_sockets, error_sockets = select.select([self.__socket], [], [], 0)
			for sock in read_sockets:
				if sock == self.__socket:
					# log.debug("Socket has data")
					return True
		
		# log.info("Socket has no data")
		
		return False
	
	def stop_listening(self):
		
		self.__logger.get().info("Making sure we're not listening")
		
		if self.__socket is not None:
			
			self.__logger.get().info("We were listening; Shutting down")
			
			self.__socket.close()
			self.__socket = None
