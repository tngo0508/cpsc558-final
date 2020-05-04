

import logging
import os
import sys


class Logger:
	
	__DEFAULT_LOGGER_NAME = "UNNAMED LOGGER!"
	
	def __init__(self, group=None, log_name=None, label=None):
		
		"""Recycled from other personal repos"""
		
		if group is None:
			raise Exception("Need the group")
		
		if log_name is None:
			raise Exception("Need the name")
		
		if label is None:
			raise Exception("Need the label")
		
		self.__group = group
		
		self.__logger = logging.getLogger(label)
		self.__logger.setLevel(logging.DEBUG)
		
		self.__logger_formatter = logging.Formatter(
			fmt="[%(name)s][%(levelname)s] [%(asctime)s] %(message)s",
			datefmt="%b %d, %Y; %I:%M%p.%S"
		)
		
		# Output to stdout
		self.__logger_console_handler = logging.StreamHandler(sys.stdout)
		self.__logger_console_handler.setFormatter(self.__logger_formatter)
		self.__logger.addHandler(self.__logger_console_handler)
		
		# Output to file
		log_file_dir = self.make_log_file_directory_path()
		log_file_name = os.path.join(
			log_file_dir,
			log_name + ".txt"
		)
		try:
			os.makedirs(log_file_dir)
		except FileExistsError:
			pass
		self.__logger_file_handler = logging.FileHandler(log_file_name, mode='w')
		self.__logger.addHandler(self.__logger_file_handler)
		
		self.set_verbose(False)
	
	def make_log_file_directory_path(self):
		
		d = os.path.join(
			os.path.dirname(__file__),
			"log",
			self.__group
		)
		
		return d
	
	def set_verbose(self, verbose):
		
		if verbose:
			
			self.__logger_console_handler.setLevel(logging.DEBUG)
			self.__logger_file_handler.setLevel(logging.DEBUG)
			
			self.__logger.debug("Logger set to verbose")
		
		else:
			self.__logger_console_handler.setLevel(logging.INFO)
			self.__logger_file_handler.setLevel(logging.INFO)
	
	def get(self):
		
		# type: () -> logging.Logger
		
		return self.__logger
	
	def heading(self, s):
		
		self.__logger.info("")
		self.__logger.info("*" * 40)
		self.__logger.info(("*" * 5) + " " + s)
		self.__logger.info("*" * 40)
		self.__logger.info("")
