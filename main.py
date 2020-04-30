#!/usr/bin/env python3


from CPSC558FinalProject import CPSC558FinalProject

from nodes.VideoServer import VideoServer
from nodes.VideoClient import VideoClient

from nodes.FileServer import FileServer
from nodes.FileClient import FileClient


import argparse
import os


def consume_arguments():
	
	# Main stuff
	parser = argparse.ArgumentParser(
		prog="CPSC 558 Final Project",
		description="Make entry point for CPSC 558 Final Project program"
	)
	
	parser.add_argument(
		"--name",
		required=False,
		dest="name",
		help="Set a name for this instance. Helpful for node programs.",
		default=None
	)
	
	parser.add_argument(
		"--run-name",
		required=True,
		dest="run_name",
		help="Set a name for this particular run (helps logging)",
		choices=["topology", "demo", "hub", "switch", "qswitch"]
	)
	
	parser.add_argument(
		"--topology", "--topo",
		required=False,
		action="store_true",
		dest="topology",
		help="Run a quick topology test and render to dot graph with graphviz"
	)
	
	parser.add_argument(
		"--run",
		required=False,
		action="store_true",
		dest="run",
		help="Run the full suite of tests"
	)
	
	parser.add_argument(
		"--video-server",
		required=False,
		action="store_true",
		dest="video_server",
		help="Start a video server instance"
	)
	
	parser.add_argument(
		"--video-client",
		required=False,
		action="store_true",
		dest="video_client",
		help="Start a video client instance"
	)
	
	parser.add_argument(
		"--file-server",
		required=False,
		action="store_true",
		dest="file_server",
		help="Start a file server instance"
	)
	
	parser.add_argument(
		"--file-client",
		required=False,
		action="store_true",
		dest="file_client",
		help="Start a file client instance"
	)
	
	parser.add_argument(
		"--directory", "--dir",
		dest="directory",
		default=None,
		help="Specify a directory (i.e., for the File Server)"
	)
	
	parser.add_argument(
		"--hostname", "--host",
		dest="hostname",
		default=None,
		help="Specify a hostname (i.e., for clients to connect to)"
	)
	
	args = parser.parse_args()
	
	return args


# Entry point
def main():
	
	args = consume_arguments()
	
	# Normal run
	if args.run:
		fp = CPSC558FinalProject(run_name=args.run_name)
		fp.run()
	
	# Topology test
	elif args.topology:
		fp = CPSC558FinalProject(run_name=args.run_name)
		fp.do_topology_test()
	
	# Video server
	elif args.video_server:
		v = VideoServer(run_name=args.run_name, name=args.name)
		v.run()
	
	# Video client
	elif args.video_client:
		v = VideoClient(run_name=args.run_name, name=args.name, server_host=args.hostname)
		v.run()
	
	# File server
	elif args.file_server:
		os.chdir(args.directory)
		f = FileServer(run_name=args.run_name, name=args.name)
		f.run()
	
	# File client
	elif args.file_client:
		f = FileClient(run_name=args.run_name, name=args.name, server_host=args.hostname)
		f.run()
	
	# Invalid args
	else:
		raise Exception("Don't really know what to do. Use --help switch for more information")


if __name__ == "__main__":
	main()
