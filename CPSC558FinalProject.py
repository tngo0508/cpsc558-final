
from Logger import Logger

from Topology import Topology
from controllers.DumbHub import DumbHub


import mininet
from mininet.net import Mininet
from mininet.node import Ryu

import os
import sys
import time


class CPSC558FinalProject:
	
	def __init__(self):
		
		self.__logger = Logger("558 Final Project")
		
		self.__net = None  # Mininet
		self.__topo = None
		self.__controller = None
		
		self.__logger.get().info("Instantiated inside Python version: " + str(sys.version))
	
	def run(self):
		
		log = self.__logger.get()
		log.info("Running main project")
		
		log.info("Instantiating custom Topology class")
		self.__topo = Topology(self.__logger)
		log.info("Rendering graph of current topology")
		self.__topo.render_dotgraph()
		
		controller = Ryu('ryu_dumb_hub', 'DumbHubController.py')
		# controller = Ryu('ryu_demo_switch', 'Demo_SimpleSwitch.py')
		
		log.info("Instantiating Mininet")
		self.__net = Mininet(
			topo=self.__topo,
			# controller=mininet.node.RemoteController,
			# controller=DumbHubController,
			# controller=mininet.node.Controller,
			controller = controller,
			waitConnected=True
		)
		self.__topo.set_net(self.__net)
		self.__topo.consume_instances()
		
		log.info("Starting Mininet (will wait for controller)")
		self.__net.start()
		log.info("Mininet found a controller to connect to")
		
		# Ping tests
		self.ping_all()
		
		# Begin video traffic
		self.start_video_traffic()
		
		#
		# self.__net.interact()
		time.sleep(60000)
		
		#
		log.info("Done!")
	
	def do_topology_test(self):
		
		log = self.__logger.get()
		log.info("Running topology test")
		
		log.info("Instantiating custom Topology class")
		self.__topo = Topology(self.__logger)
		
		log.info("Instantiating Mininet")
		self.__net = Mininet(
			topo=self.__topo,
			controller=mininet.node.RemoteController
		)
		self.__topo.set_net(self.__net)
		self.__topo.consume_instances()
		
		log.info("Rendering graph of current topology")
		self.__topo.render_dotgraph(False)
		
		log.info("Done!")
	
	def init_dumb_hub(self):
	
		# DumbHub()
		pass
	
	def ping_all(self):
		
		self.__logger.get().info("Attempting to ping between all nodes")
		self.__net.pingAll(timeout=1)
		self.__logger.get().info("Done pinging between all nodes")
	
	def run_dumb_hub(self):
		
		log = self.__logger.get()
		log.info("Running dumb hub controller (Ryu)")
	
	def run_simple_switch(self):
		
		log = self.__logger.get()
		log.info("Running simple switch controller (Ryu)")
	
	@staticmethod
	def make_process_stdout_file_path(file_name, clear=True):
		
		output_dir = os.path.join(
			os.path.dirname(__file__),
			"log"
		)
		try:
			os.makedirs(output_dir)
		except FileExistsError:
			pass
		
		file_path = os.path.join(
			output_dir,
			file_name + ".txt"
		)
		if clear and os.path.isfile(file_path):
			os.unlink(file_path)
		
		return file_path
	
	def start_video_traffic(self):
		
		log = self.__logger.get()
		
		log.info("Starting video traffic")
		
		server_log_file = self.make_process_stdout_file_path("video-server")
		client_log_file = self.make_process_stdout_file_path("video-clients")
		
		# Start server
		server = self.__topo.get_video_server_instance()
		server.cmd("ifconfig | grep eth >> " + server_log_file + " 2>&1")
		server.sendCmd("./main.py --video-server >> " + server_log_file + " 2>&1")
		
		# Start clients
		clients = list(self.__topo.get_video_client_instances().values())
		for client in clients:
			client.cmd("ifconfig | grep eth >> " + client_log_file + " 2>&1")
			client.sendCmd("./main.py --video-client >> " + client_log_file + " 2>&1")
		
		log.info("Done starting video traffic")
