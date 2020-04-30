

from Logger import Logger


import requests
import subprocess


class FileClient:
	
	# Sorry not sorry
	__default_server_host = "10.0.0.2"
	__default_server_port = 8012
	
	#
	__default_request_timeout = 5
	
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
			server_host = self.__default_server_host
		self.__server_host = server_host
		
		if server_port is None:
			server_port = self.__default_server_port
		self.__server_port = server_port
	
	def run(self):
	
		log = self.__logger.get()
		
		log.info("Running!")
		
		url = "http://" + self.__server_host + ":" + str(self.__server_port) + "/random-data.dat"
		
		try:
			log.info("Trying to download url: " + url)
			r = requests.get(url, timeout=self.__default_request_timeout)
		except requests.exceptions.ConnectionError:
			log.error("Failed to download url: " + url)
			return
		
		response_data = r.content
		log.info("Got " + str(len(response_data)) + " bytes of data")
		
		log.info("Done!")
