

from Logger import Logger
from Benchmarker import Benchmarker

import socket
import subprocess
import time


class TattleTail:
	
	def __init__(self, run_name, name):
		
		self.__run_name = run_name
		self.__name = name
		
		my_ip = subprocess.check_output(["hostname", "-I"]).decode().strip()
		self.__logger = Logger(
			group=run_name,
			log_name=name,
			label="TattleTail " + my_ip
		)
		
		self.__benchmarker = Benchmarker(name)
	
	def __str__(self):
		
		s = ""
		
		s += "TattleTail Instance"
		# s += "; MAC = " + self.__host.MAC()
		# s += "; IP = " + self.__host.IP()
		
		return s
	
	def __del__(self):
		
		log = self.__logger.get()
		
		log.info("Oh noes! They're deleting meeeeeeee !")
		log.info(self.__benchmarker)
	
	def run(self):
	
		log = self.__logger.get()
		
		log.info("Running!")
		
		self.snoop_a_loop()
		
		log.info("Done running")
	
	def snoop_a_loop(self):
		
		# Create a promiscuous socket
		log = self.__logger.get()
		
		log.info("Creating promiscuous socket")
		sock = socket.socket(socket.AF_PACKET, socket.SOCK_DGRAM)
		sock.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
		
		# Attempt to receive any data, indefinitely
		self.__benchmarker.start()
		while True:
			
			received, sender = sock.recv(1048576)
			self.__benchmarker.increased_bytes_received(len(received))
			
			log.debug(
				"Received " + str(len(received)) + " bytes from" + str(sender)
				+ "; Total = " + str(self.__benchmarker.get_bytes_received())
			)
