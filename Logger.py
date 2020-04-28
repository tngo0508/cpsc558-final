

import logging
import sys


class Logger:
	
	__DEFAULT_LOGGER_NAME = "UNNAMED LOGGER!"
	
	__verbose = False
	
	def __init__(self, name=None):
		
		"""Recycled from other personal repos"""
		
		if name is None:
			name = self.__DEFAULT_LOGGER_NAME
		
		self.__logger = logging.getLogger(name)
		self.__logger.setLevel(logging.DEBUG)
		
		self.__logger_formatter = logging.Formatter(
			fmt="[%(name)s][%(levelname)s] [%(asctime)s] %(message)s",
			datefmt="%b %d, %Y; %I:%M%p.%S"
		)
		
		self.__logger_console_handler = logging.StreamHandler(sys.stdout)
		self.__logger_console_handler.setFormatter(self.__logger_formatter)
		self.__logger.addHandler(self.__logger_console_handler)
		
		self.set_verbose(False)
	
	def set_verbose(self, verbose):
		
		if verbose:
			
			self.__logger_console_handler.setLevel(logging.DEBUG)
			
			self.__logger.debug("Logger set to verbose")
		
		else:
			self.__logger_console_handler.setLevel(logging.INFO)
	
	def get(self):
		
		# type: () -> logging.Logger
		
		return self.__logger
