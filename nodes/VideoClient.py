

from Logger import Logger


import select
import socket
import subprocess
import threading
import time


class VideoClient:
	
	# Sorry not sorry
	__default_server_host = "10.0.0.3"
	__default_server_port = 8013
	
	#
	__server_host = None
	__server_port = None
	
	#
	__socket = None
	__listener_thread = None
	
	__wanted_data_size_megabytes = 100
	__beg_string = "MOAR PLZ!\n".encode()
	
	__benchmark_is_running = False
	__benchmark_start_time = 0
	__benchmark_end_time = 0
	__benchmark_elapsed_time = 0
	__benchmark_bytes_received = 0
	__benchmark_bytes_per_second = 0
	__benchmark_megabites_per_second = 0
	
	def __init__(self, run_name, name, host=None, port=None):
		
		my_ip = subprocess.check_output(["hostname", "-I"]).decode().strip()
		
		if name is None:
			name = my_ip
		
		self.__logger = Logger(
			group=run_name,
			log_name=name,
			label="VideoClient"
		)
		
		if host is None:
			host = self.__default_server_host
		self.__server_host = host
		
		if port is None:
			port = self.__default_server_port
		self.__server_port = port
		
		# self.__logger.set_verbose(True)
		
	def __del__(self):
		
		if threading.current_thread == threading.main_thread() and self.__listener_thread:
			
			self.__listener_thread.join()
			self.__listener_thread = None
	
	def run(self):
		
		log = self.__logger.get()
		
		log.info("Running ...")
		
		self.init_socket()
		self.leech_loop()
		
		log.info("Finished running")
		
	def init_socket(self):
		
		self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		# self.__socket.bind((self.__server_host, self.__server_port))
	
	def init_data_receiver(self):
		
		self.__listener_thread = threading.Thread(target=self.data_receiver)
		self.__listener_thread.start()
	
	def data_receiver(self):
		
		log = self.__logger.get()
		
		while self.__benchmark_is_running:
			
			# log.info("Data receiver iteration")
			
			if self.socket_has_data():
				
				# log.info("Receiving ... ")
				
				received, sender = self.__socket.recvfrom(1048576)
				self.__benchmark_bytes_received += len(received)
				
				log.debug(
					"Received " + str(len(received)) + " bytes from" + str(sender)
					+ "; Total = " + str(self.__benchmark_bytes_received)
				)
				
			else:
				time.sleep(.001)
	
	def leech_loop(self):
		
		log = self.__logger.get()
		
		wanted_bytes = self.__wanted_data_size_megabytes * 1048576
		
		log.info("Begin leech loops")
		
		self.start_benchmark()
		self.init_data_receiver()
		while self.__benchmark_bytes_received < wanted_bytes:
			
			if not self.socket_has_data():
				self.ask_server_for_data()
			else:
				log.debug("Have data ... will wait")
			
			time.sleep(.001)
		
		self.stop_benchmark()
		
		log.info("End leech loops")
	
	def ask_server_for_data(self):
		
		# log = self.__logger.get()
		
		# log.debug("Asking server for data: " + str(self.__server_host) + "::" + str(self.__server_port))
		self.__socket.sendto(self.__beg_string, (self.__server_host, self.__server_port))
		# log.debug("Done asking server for data")
		
	def socket_has_data(self):
		
		# log = self.__logger.get()
		
		# log.debug("Checking socket for data")
		if self.__socket:
			read_sockets, write_sockets, error_sockets = select.select([self.__socket], [], [], 0)
			for sock in read_sockets:
				if sock == self.__socket:
					# log.debug("Socket has data")
					return True
		
		# log.debug("Socket has no data")
		
		return False
	
	def stop_listening(self):
		
		self.__logger.get().info("Making sure we're not listening")
		
		if self.__socket is not None:
			self.__logger.get().info("We were listening; Shutting down")
			
			self.__socket.close()
			self.__socket = None
	
	def start_benchmark(self):
		
		self.__benchmark_is_running = True
		self.__benchmark_start_time = self.timestamp_millis()
		self.__benchmark_end_time = self.__benchmark_start_time
		self.__benchmark_elapsed_time = 0
		self.__benchmark_bytes_received = 0
		self.__benchmark_bytes_per_second = 0
	
	def stop_benchmark(self):
		
		# log = self.__logger.get()
		
		self.__benchmark_is_running = False
		self.__benchmark_end_time = self.timestamp_millis()
		
		self.__benchmark_elapsed_time = (
			float(self.__benchmark_end_time - self.__benchmark_start_time)
			/
			1000.0
		)
		
		# log.info(str(self.__benchmark_start_time))
		# log.info(str(self.__benchmark_end_time))
		# log.info(str(self.__benchmark_bytes_received))
		# log.info(str(self.__benchmark_elapsed_time))
		self.__benchmark_bytes_per_second = self.__benchmark_bytes_received / self.__benchmark_elapsed_time
		self.__benchmark_megabites_per_second = (
			self.__benchmark_bytes_per_second / 131072
		)
		
		self.__logger.get().info(
			"Benchmark: " + str(self.__benchmark_bytes_received / 1048576) + " megabytes received"
		)
		self.__logger.get().info(
			"Benchmark: " + str(self.__benchmark_megabites_per_second) + " megabits per second"
		)
	
	@staticmethod
	def timestamp_millis():
		
		return time.time() * 1000
