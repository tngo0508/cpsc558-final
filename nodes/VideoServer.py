

from nodes.ServerBase import ServerBase

import socket


class VideoServer(ServerBase):
	
	__listen_port = 8012
	
	def __init__(self, run_name, name):
		
		super(VideoServer, self).__init__(
			run_name,
			name,
			socket.SOCK_DGRAM, None, self.__listen_port
		)
	
	def run(self):
		
		self.start_listener_loop()
	
	def start_listener_loop(self):
		
		log = self.logger().get()
		sock = self.socket()
		
		reply_data = "Z" * 1024
		reply_data = reply_data.encode()
		
		log.info("Begin listener loop")
		while True:
			
			data, sender = sock.recvfrom(1024)
			log.info("Received " + str(len(data)) + " bytes from " + str(sender) + "; Sending data")
			
			# Send back some megabytes
			for i in range(1024):
				sock.sendto(reply_data, sender)
			log.info("Done sending data to " + str(sender))


def main():
	
	v = VideoServer()


if __name__ == "__main__":
	main()
