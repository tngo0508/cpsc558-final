

from Logger import Logger


import http.server
import os
import subprocess


class FileServer:
	
	__DEFAULT_LISTEN_PORT = 8012
	
	def __init__(self, run_name, name, listen_port=None):
		
		self.__run_name = run_name
		self.__name = name
		
		if listen_port is None:
			listen_port = self.__DEFAULT_LISTEN_PORT
		self.__port = listen_port
		
		self.__directory = os.getcwd()
		
		my_ip = subprocess.check_output(["hostname", "-I"]).decode().strip()
		self.__logger = Logger(
			group=run_name,
			log_name=name,
			label="FileServer " + my_ip + "::" + str(listen_port)
		)
	
	def run(self):
		
		log = self.__logger.get()
		
		log.info("Run!")
		
		self.start_server()
		
		log.info("Done running")
	
	def start_server(self):
		
		log = self.__logger.get()
		
		log.info("Starting Python3 HTTPServer in directory: " + str(self.__directory))
		log.info("Will listen on port: " + str(self.__port))
		
		the_handler = http.server.SimpleHTTPRequestHandler
		the_server = http.server.HTTPServer(('', self.__port), the_handler)
		# the_server = http.server.ThreadingHTTPServer(('', self.__port), the_handler)
		# Can't use ThreadingHTTPServer because our Python is too old!
		
		the_server.serve_forever()
		
		log.info("Somehow exited the HTTPServer")
