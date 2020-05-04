
from Logger import Logger

from Topology import Topology
from controllers.DumbHub import DumbHub


import mininet
from mininet.net import Mininet
from mininet.link import TCIntf
from mininet.util import custom as mininet_custom

from mininet.node import Ryu

import os
import re
import sys


class CPSC558FinalProject:
	
	__DEFAULT_RUN_NAME = "main"
	__DEFAULT_FILE_SERVER_DIRECTORY = "data"
	
	__BANDWIDTH_LIMIT_MBPS = 1000
	__BANDWIDTH_LIMIT_LATENCY = "1ms"
	
	def __init__(self, run_name):
		
		self.__run_name = run_name
		
		self.__logger = Logger(
			group=self.__run_name,
			log_name=__name__,
			label="558 Project"
		)
		
		self.__logger_summary = Logger(
			group="summary",
			log_name=__name__,
			label="558 Project Summary",
			append=True
		)
		
		self.__net = None  # Mininet
		self.__topo = None
		self.__controller = None
		
		self.__logger.get().info("Instantiated inside Python version: " + str(sys.version))
	
	def run(self):
		
		log = self.__logger.get()
		
		controller_log_file = os.path.join(
			self.__logger.make_log_file_directory_path(),
			"controller.txt"
		)
		
		controller_name = "ryu_" + self.__run_name
		controller_path_relative = "controllers/"
		if self.__run_name == "demo":
			controller_source_file_name = "Demo_SimpleSwitch.py"
		elif self.__run_name == "hub":
			controller_source_file_name = "DumbHub.py"
		elif self.__run_name == "switch":
			controller_source_file_name = "SimpleSwitch.py"
		elif self.__run_name == "qswitch":
			controller_source_file_name = "QSwitch.py"
		else:
			raise Exception("Invalid run name: " + str(self.__run_name))
		controller_path_relative += controller_source_file_name
		
		# Instantiate Mininet::Ryu(), which just launches ryu-manager for us
		controller = Ryu(
			controller_name, controller_path_relative,
			# "--verbose",
			"--log-file", controller_log_file
		)
		
		self.__logger.heading("Running with controller: " + controller_source_file_name)
		
		log.info("Instantiating custom Topology class")
		self.__topo = Topology(self.__logger)
		log.info("Rendering graph of current topology")
		self.__topo.render_dotgraph()
		
		self.run_with_controller(controller)
		
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
		self.start_tattle_tail(True)
		self.start_file_traffic(True)
		self.start_video_traffic(True)
		
		#
		self.wait_for_hosts_to_finish()
		self.summarize_node_logs()
	
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
	
	def start_tattle_tail(self, use_log: bool = True):
		
		log = self.__logger.get()
		
		log.info("Starting tattle tail")
		
		log_file = self.make_process_stdout_file_path(self.__run_name, "tattle-tail-stdout")
		log.info(log_file)
		
		# Get tattle tail instance
		tattle = self.__topo.get_tattle_tail_instance()
		tattle_ip = tattle.IP()
		log.info("Tattle tail IP is: " + str(tattle_ip))
		
		# Start the tattle tail
		if use_log:
			tattle.cmd("ifconfig | grep eth >> \"" + log_file + "\" 2>&1")
			tattle.sendCmd(
				"./main.py --tattle-tail"
				+ " --run-name \"" + str(self.__run_name) + "\""
				+ " --name \"" + str(tattle) + "\""
				+ " >> \"" + log_file + "\" 2>&1"
			)
		else:
			tattle.cmd("ifconfig | grep eth 2>&1")
			tattle.sendCmd(
				"./main.py --tattle-tail"
				+ " --run-name \"" + str(self.__run_name) + "\""
				+ " --name \"" + str(tattle) + "\""
				+ " 2>&1"
			)
		
		log.info("Done starting tattle tail")
	
	def start_video_traffic(self, use_log: bool = True):
		
		log = self.__logger.get()
		
		log.info("Starting video traffic")
		
		server_log_file = self.make_process_stdout_file_path(self.__run_name, "video-server-stdout")
		log.info("Video server stdout: " + server_log_file)
		client_log_file = self.make_process_stdout_file_path(self.__run_name, "video-clients-stdout")
		log.info("Video clients stdout: " + client_log_file)
		
		# Get video server instance
		server = self.__topo.get_video_server_instance()
		server_ip = server.IP()
		log.info("Video server IP is: " + str(server_ip))
		
		# Start video server
		if use_log:
			server.cmd("ifconfig | grep eth >> \"" + server_log_file + "\" 2>&1")
			server.sendCmd(
				"./main.py --video-server"
				+ " --run-name \"" + str(self.__run_name) + "\""
				+ " --name \"" + str(server) + "\""
				+ " >> \"" + server_log_file + "\" 2>&1"
			)
		else:
			server.cmd("ifconfig | grep eth 2>&1")
			server.sendCmd(
				"./main.py --video-server"
				+ " --run-name \"" + str(self.__run_name) + "\""
				+ " --name \"" + str(server) + "\""
				+ " 2>&1"
			)
		
		# Grab client instances
		clients = list(self.__topo.get_video_client_instances().values())
		
		# Start each client
		for client in clients:
			
			if use_log:
				client.cmd("ifconfig | grep eth >> \"" + client_log_file + "\" 2>&1")
				client.sendCmd(
					"./main.py --video-client"
					+ " --run-name \"" + str(self.__run_name) + "\""
					+ " --name \"" + str(client) + "\""
					+ " --host \"" + server_ip + "\""
					+ " >> \"" + client_log_file + "\" 2>&1"
				)
			else:
				client.cmd("ifconfig | grep eth 2>&1")
				client.sendCmd(
					"./main.py --video-client"
					+ " --run-name \"" + str(self.__run_name) + "\""
					+ " --name \"" + str(client) + "\""
					+ " --host \"" + server_ip + "\""
					+ " 2>&1"
				)
		
		log.info("Done starting video traffic")
	
	def start_file_traffic(self, use_log: bool = True):
		
		log = self.__logger.get()
		
		log.info("Starting file traffic")
		
		server_log_file = self.make_process_stdout_file_path(self.__run_name, "file-server-stdout")
		log.info("File server stdout: " + server_log_file)
		client_log_file = self.make_process_stdout_file_path(self.__run_name, "file-clients-stdout")
		log.info("File clients stdout: " + client_log_file)
		
		# Get file server instance
		server = self.__topo.get_file_server_instance()
		server_ip = server.IP()
		log.info("File server IP is: " + str(server_ip))
		
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
		
		# Grab client instances
		clients = list(self.__topo.get_file_client_instances().values())
		
		# Start each client
		for client in clients:
			
			if use_log:
				client.cmd("ifconfig | grep eth >> \"" + client_log_file + "\" 2>&1")
				client.sendCmd(
					"./main.py --file-client"
					+ " --run-name \"" + str(self.__run_name) + "\""
					+ " --name \"" + str(client) + "\""
					+ " --host \"" + server_ip + "\""
					+ " >> \"" + client_log_file + "\" 2>&1"
				)
			else:
				client.cmd("ifconfig | grep eth 2>&1")
				client.sendCmd(
					"./main.py --file-client"
					+ " --run-name \"" + str(self.__run_name) + "\""
					+ " --name \"" + str(client) + "\""
					+ " --host \"" + server_ip + "\""
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
	
	def summarize_node_logs(self):
		
		self.summarize_node_benchmark_logs()
	
	def summarize_node_benchmark_logs(self):
		
		log = self.__logger.get()
		log_s = self.__logger_summary.get()
		
		log.info("Attempting to summarize node benchmark logs")
		
		log_s.info("")
		log_s.info("*** " + self.__run_name + " ***")
		log_s.info("Attempting to summarize node benchmark logs")
		
		logs_dir = self.__logger.make_log_file_directory_path()
		log.info("Pulling from log directory: " + logs_dir)
		
		# Build a list of all nodes we're interested in
		nodes_file_clients = list(self.__topo.get_file_client_instances().values())
		nodes_video_clients = list(self.__topo.get_video_client_instances().values())
		nodes_all_clients = nodes_file_clients + nodes_video_clients
		log.info("Will examine logs from " + str(len(nodes_all_clients)) + " client nodes")
		
		pattern_bytes_received = re.compile("""^Bytes received: (?P<bytes>[0-9]+)$""", re.MULTILINE | re.IGNORECASE)
		pattern_mbps = re.compile("""^Megabits per second: (?P<mbps>[0-9.]+)$""", re.MULTILINE | re.IGNORECASE)
		
		# For each client we're interested in, pull the number of bytes transferred from its logs
		total_bytes = 0
		mbps_all_samples = list()
		mbps_file_samples = list()
		mbps_video_samples = list()
		for node in nodes_all_clients:
			
			node_log_file_name = str(node) + ".txt"
			
			log_path = os.path.join(logs_dir, node_log_file_name)
			
			log.info("Examining log for node \"" + str(node) + "\": " + node_log_file_name)
			
			# Load the logfile
			with open(log_path, "rt") as f:
				
				s = f.read()
				
				# Bytes received
				match = pattern_bytes_received.search(s)
				if match is None:
					raise Exception("Failed to parse node; Cannot find bytes received!")
				node_bytes = int(match.group("bytes"))
				total_bytes += node_bytes
				log.info(
					"Node \"" + str(node) + "\" seems to have received " + str(node_bytes) + " bytes"
					+ " (" + str(total_bytes) + " total)"
				)
				
				# Megabits per second
				match = pattern_mbps.search(s)
				if match is None:
					raise Exception("Failed to parse node; Cannot find megabits per second!")
				node_mbps = float(match.group("mbps"))
				log.info(
					"Node \"" + str(node) + "\" seems to have received data at " + str(node_mbps) + " megabits per second"
				)
				
				# Add to sample pools
				mbps_all_samples.append(node_mbps)
				if node in nodes_file_clients:
					mbps_file_samples.append(node_mbps)
				elif node in nodes_video_clients:
					mbps_video_samples.append(node_mbps)
				else:
					raise Exception("Don't know where to add this node's bandwidth sample!")
		
		mbps_average_file = sum(mbps_file_samples) / len(mbps_file_samples)
		mbps_average_video = sum(mbps_video_samples) / len(mbps_video_samples)
		mbps_average_all = sum(mbps_all_samples) / len(mbps_all_samples)
		
		log.info("We seem to have the following aggregate bandwidths:")
		log_s.info("We seem to have the following aggregate bandwidths:")
		log.info("File clients: " + str(mbps_average_file) + " mbps")
		log_s.info("File clients: " + str(mbps_average_file) + " mbps")
		log.info("Video clients: " + str(mbps_average_video) + " mbps")
		log_s.info("Video clients: " + str(mbps_average_video) + " mbps")
		log.info("All clients: " + str(mbps_average_all) + " mbps")
		log_s.info("All clients: " + str(mbps_average_all) + " mbps")
