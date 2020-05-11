

from Logger import Logger
from Benchmarker import Benchmarker


import requests
import subprocess


class FileClient:
	
	# Sorry not sorry
	__default_server_port = 8012
	
	#
	__default_request_timeout = 2
	__default_request_retries = 100
	
	#
	__downloads_count = 5
	
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
		
		self.__benchmarker.start()
		
		for i in range(self.__downloads_count):
			self.do_one_download(i + 1)
		
		self.__benchmarker.stop()
		log.info(self.__benchmarker)
		
		log.info(self.__benchmarker)
		
		log.info("Done!")
	
	def do_one_download(self, run_number):
		
		log = self.__logger.get()
		
		log.info("do_one_download() - Run #" + str(run_number))
		
		url = "http://" + self.__server_host + ":" + str(self.__server_port) + "/random-data.dat"
		
		success = False
		any_fails = False
		r = None
		for j in range(self.__default_request_retries):
			
			if any_fails:
				log.info("Trying again, I guess; Attempt #" + str(j + 1) + " ...")
			
			try:
				log.info("Trying to download url: " + url)
				r = requests.get(url, timeout=self.__default_request_timeout)
				log.info("Successfully downloaded url")
				success = True
				break
			except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout, TypeError):
				log.error("Error trying to download url: " + url)
				any_fails = True
		
		if success is True:
			response_data = r.content
		else:
			log.info("Failed to download url: " + url)
			response_data = ""
		
		self.__benchmarker.increased_bytes_received(len(response_data))
