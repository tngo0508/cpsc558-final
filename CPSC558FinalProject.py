
from Logger import Logger

from Topology import Topology
from controllers.DumbHub import DumbHub


import mininet
from mininet.net import Mininet
from mininet.clean import Cleanup
from mininet.node import Ryu

import os
import sys
import time


class CPSC558FinalProject:
	
	__DEFAULT_RUN_NAME = "main"
	__DEFAULT_FILE_SERVER_DIRECTORY = "data"
	
	def __init__(self, run_name):
		
		self.__run_name = run_name
		
		self.__logger = Logger(
			group=run_name,
			log_name=__name__,
			label="558 Final Project"
		)
		
		self.__net = None  # Mininet
		self.__topo = None
		self.__controller = None
		
		self.__logger.get().info("Instantiated inside Python version: " + str(sys.version))
	
	def run(self):
		
		log = self.__logger.get()
		
		self.__logger.heading("Running test with: " + self.__run_name)
		
		log.info("Running main project")
		
		log.info("Instantiating custom Topology class")
		self.__topo = Topology(self.__logger)
		log.info("Rendering graph of current topology")
		self.__topo.render_dotgraph()
		
		# Instantiate some controllers we can choose to run with
		controllers = dict({
			
			"demo": ("Demo Switch", Ryu('ryu_demo_switch', 'controllers/Demo_SimpleSwitch.py')),
			"hub": ("Dumb Hub", Ryu('ryu_dumb_hub', 'controllers/DumbHub.py')),
			"switch": ("Simple Switch", Ryu('ryu_simple_switch', 'controllers/SimpleSwitch.py')),
			"qswitch": ("QoS Switch", Ryu('ryu_qswitch', 'controllers/QSwitch.py'))
		})
		
		if self.__run_name in controllers.keys():
			
			controller_name, controller = controllers[self.__run_name]
			
			self.run_with_controller(controller)
			
		else:
			raise Exception("Invalid run name: " + str(self.__run_name))
		
		#
		log.info("Done")
	
	def run_with_controller(self, controller):
		
		log = self.__logger.get()
		
		log.info("Instantiating Mininet")
		
		self.__net = Mininet(
			topo=self.__topo,
			controller=controller,
			waitConnected=False
		)
		self.__topo.set_net(self.__net)
		self.__topo.consume_instances()
		
		log.info("Starting Mininet (will wait for controller)")
		self.__net.start()
		wait_result = self.__net.waitConnected(timeout=10)
		if wait_result is False:
			log.error("Failed to wait for a controller!")
			log.error("FAIL")
			return
		log.info("Mininet found a controller to connect to")
		
		# Ping tests
		self.ping_all()
		
		# Begin node traffic
		self.start_file_traffic(True)
		self.start_video_traffic(True)
		
		#
		self.wait_for_hosts_to_finish()
	
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
	
	def ping_all(self):
		
		self.__logger.get().info("Attempting to ping between all nodes")
		self.__net.pingAll(timeout=1)
		print()
		self.__logger.get().info("Done pinging between all nodes")
	
	@staticmethod
	def make_process_stdout_file_path(run_name, file_name, clear=True):
		
		output_dir = os.path.join(
			os.path.dirname(__file__),
			"log",
			run_name
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
	
	def start_video_traffic(self, use_log: bool = True):
		
		log = self.__logger.get()
		
		log.info("Starting video traffic")
		
		server_log_file = self.make_process_stdout_file_path(self.__run_name, "video-server-stdout")
		log.info(server_log_file)
		client_log_file = self.make_process_stdout_file_path(self.__run_name, "video-clients-stdout")
		log.info(client_log_file)
		
		# Create video server instance
		server = self.__topo.get_video_server_instance()
		
		# Start video server
		if use_log:
			server.cmd("ifconfig | grep eth >> \"" + server_log_file + "\" 2>&1")
			server.sendCmd("./main.py --video-server --run-name \"" + str(self.__run_name) + "\" --name \"" + str(server) + "\" >> \"" + server_log_file + "\" 2>&1")
		else:
			server.cmd("ifconfig | grep eth 2>&1")
			server.sendCmd("./main.py --video-server --run-name \"" + str(self.__run_name) + "\" --name \"" + str(server) + "\" 2>&1")
		
		# Instantiate clients
		clients = list(self.__topo.get_video_client_instances().values())
		
		# Start each client
		for client in clients:
			
			if use_log:
				client.cmd("ifconfig | grep eth >> \"" + client_log_file + "\" 2>&1")
				client.sendCmd("./main.py --video-client --run-name \"" + str(self.__run_name) + "\" --name \"" + str(client) + "\" >> \"" + client_log_file + "\" 2>&1")
			else:
				client.cmd("ifconfig | grep eth 2>&1")
				client.sendCmd("./main.py --video-client --run-name \"" + str(self.__run_name) + "\" --name \"" + str(client) + "\" 2>&1")
		
		log.info("Done starting video traffic")
	
	def start_file_traffic(self, use_log: bool = True):
		
		log = self.__logger.get()
		
		log.info("Starting file traffic")
		
		server_log_file = self.make_process_stdout_file_path(self.__run_name, "file-server-stdout")
		log.info(server_log_file)
		client_log_file = self.make_process_stdout_file_path(self.__run_name, "file-clients-stdout")
		log.info(client_log_file)
		
		# Create file server instance
		server = self.__topo.get_file_server_instance()
		
		# Start file server
		if use_log:
			server.cmd("ifconfig | grep eth >> \"" + server_log_file + "\" 2>&1")
			server.sendCmd(
				"./main.py --file-server"
				+ " --run-name \"" + str(self.__run_name) + "\""
				+ " --name \"" + str(server) + "\""
				+ " --directory \"" + self.make_file_server_directory() + "\""
				+ " >> \"" + server_log_file + "\" 2>&1"
			)
		else:
			server.cmd("ifconfig | grep eth 2>&1")
			server.sendCmd(
				"./main.py --file-server"
				+ " --run-name \"" + str(self.__run_name) + "\""
				+ " --name \"" + str(server) + "\""
				+ " --directory \"" + self.make_file_server_directory() + "\""
				+ " 2>&1"
			)
		
		# Instantiate clients
		clients = list(self.__topo.get_file_client_instances().values())
		
		# Start each client
		for client in clients:
			
			if use_log:
				client.cmd("ifconfig | grep eth >> \"" + client_log_file + "\" 2>&1")
				client.sendCmd(
					"./main.py --file-client"
					+ " --run-name \"" + str(self.__run_name) + "\""
					+ " --name \"" + str(client) + "\""
					+ " >> \"" + client_log_file + "\" 2>&1"
				)
			else:
				client.cmd("ifconfig | grep eth 2>&1")
				client.sendCmd(
					"./main.py --file-client"
					+ " --run-name \"" + str(self.__run_name) + "\""
					+ " --name \"" + str(client) + "\""
					+ " 2>&1"
				)
		
		log.info("Done starting file traffic")
	
	def wait_for_hosts_to_finish(self):
		
		log = self.__logger.get()
		
		log.info("Start waiting for all hosts to finish")
		
		# Gather all hosts to wait for
		hosts_to_wait_for = list()
		for host_name in self.__topo.get_video_client_instances():
			hosts_to_wait_for.append(self.__net.nameToNode[host_name])
		for host_name in self.__topo.get_file_client_instances():
			hosts_to_wait_for.append(self.__net.nameToNode[host_name])
		
		# Wait for all the hosts
		for host in hosts_to_wait_for:
			log.info("Waiting for host " + str(host) + " to finish its command")
			host.waitOutput(verbose=True)
			log.info("Host " + str(host) + " has finished its command")
		
		log.info("Done waiting for all hosts to finish")
	
	def make_file_server_directory(self):
		
		d = os.path.join(
			os.path.dirname(__file__),
			self.__DEFAULT_FILE_SERVER_DIRECTORY
		)
		
		return d
