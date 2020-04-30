

import time


class Benchmarker:
	
	__is_running = None
	__start_time = None
	__end_time = None
	__bytes_received = None
	
	def __init__(self, label):
		
		self.__label = label
		
		self.reset()
	
	def __str__(self):
	
		s = ""
		
		s += type(self).__name__ + " for " + self.__label
		
		if self.__is_running:
			s += "\n(Benchmark is still running)"
		
		s += "\nBytes received: " + str(self.__bytes_received)
		s += "\nMegabytes received: " + str(self.get_megabytes_received())
		s += "\nMegabits per second: " + str(self.get_megabits_per_second())
		
		if not self.__is_running:
			s += "\nFinished in " + str(self.get_elapsed_seconds()) + " seconds"
		
		return s
	
	def reset(self):
		
		self.__is_running = False
		self.__start_time = 0
		self.__end_time = 0
		self.__bytes_received = 0
	
	def start(self):
		
		self.reset()
		
		self.__is_running = True
		self.__start_time = self.timestamp_millis()
		self.__end_time = self.__start_time
		self.__bytes_received = 0
	
	def stop(self):
		
		self.__end_time = self.timestamp_millis()
		
		self.__is_running = False
	
	def is_running(self):
		
		return self.__is_running
	
	@staticmethod
	def timestamp_millis():
		
		return time.time() * 1000
	
	def set_bytes_received(self, n):
	
		self.__bytes_received = n
	
	def increased_bytes_received(self, n):
		
		self.set_bytes_received(
			self.get_bytes_received() + n
		)
	
	def get_end_time(self):
	
		if self.__is_running:
			return self.timestamp_millis()
		
		return self.__end_time
	
	def get_elapsed_seconds(self):
		
		end_time = self.get_end_time()
		
		return (
			float(end_time - self.__start_time)
			/
			1000.0
		)
	
	def get_bytes_received(self):
		
		return self.__bytes_received
	
	def get_megabytes_received(self):
		
		return self.__bytes_received / 1048576
	
	def get_bytes_per_second(self):
		
		seconds = self.get_elapsed_seconds()
		if seconds > 0:
			return self.__bytes_received / seconds
		
		return 0
	
	def get_megabits_per_second(self):
		
		bps = self.get_bytes_per_second()
		
		mbps = bps / 131072
		
		return mbps
