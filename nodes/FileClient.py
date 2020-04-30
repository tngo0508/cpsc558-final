

from Logger import Logger
from Benchmarker import Benchmarker


import requests
import subprocess


class FileClient:
	
	# Sorry not sorry
	__default_server_port = 8012
	
	#
	__default_request_timeout = 5
	__default_request_retries = 100
	
	def __init__(self, run_name=None, name=None, server_host=None, server_port=None):
		
		self.__run_name = run_name
		self.__name = name
		
		my_ip = subprocess.check_output(["hostname", "-I"]).decode().strip()
		self.__logger = Logger(
			group=run_name,
			log_name=name,
			label="FileClient " + my_ip
		)
		
		if server_host is None:
			raise Exception("Please provide a hostname to connect to")
		self.__server_host = server_host
		
		if server_port is None:
			server_port = self.__default_server_port
		self.__server_port = server_port
		
		self.__benchmarker = Benchmarker(name)
	
	def run(self):
	
		log = self.__logger.get()
		
		log.info("Running!")
		
		url = "http://" + self.__server_host + ":" + str(self.__server_port) + "/random-data.dat"
		
		self.__benchmarker.start()
		
		success = False
		any_fails = False
		r = None
		for i in range(self.__default_request_retries):
			
			if any_fails:
				log.info("Trying again, I guess; Attempt #" + str(i + 1) + " ...")
			
			try:
				log.info("Trying to download url: " + url)
				r = requests.get(url, timeout=self.__default_request_timeout)
				log.info("Successfully downloaded url")
				success = True
				break
			except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout, TypeError):
				log.error("Failed to download url: " + url)
				any_fails = True
		
		if not success:
			log.info("Failed to download url: " + url)
			return
		
		response_data = r.content
		self.__benchmarker.set_bytes_received(len(response_data))
		self.__benchmarker.stop()
		
		log.info(self.__benchmarker)
		
		log.info("Done!")
