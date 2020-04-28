#!/usr/bin/env python3

import argparse

from CPSC558FinalProject import CPSC558FinalProject

from VideoServer import VideoServer
from VideoClient import VideoClient


def consume_arguments():
	
	# Main stuff
	parser = argparse.ArgumentParser(
		prog="CPSC 558 Final Project",
		description="Make entry point for CPSC 558 Final Project program"
	)
	
	parser.add_argument(
		"--topology", "--topo",
		required=False,
		action="store_true",
		dest="topology",
		help="Run a quick topology test and render to dot graph with graphviz"
	)
	
	parser.add_argument(
		"--dumb-hub", "--hub",
		required=False,
		action="store_true",
		dest="dumb_hub"
	)
	
	parser.add_argument(
		"--simple-switch",
		required=False,
		action="store_true",
		dest="simple_switch"
	)
	
	parser.add_argument(
		"--run",
		required=False,
		action="store_true",
		dest="run"
	)
	
	parser.add_argument(
		"--video-server",
		required=False,
		action="store_true",
		dest="video_server"
	)
	
	parser.add_argument(
		"--video-client",
		required=False,
		action="store_true",
		dest="video_client"
	)
	
	args = parser.parse_args()
	
	return args


# Entry point
def main():
	
	args = consume_arguments()
	
	fp = CPSC558FinalProject()
	
	if args.run:
		fp.run()
	elif args.simple_switch:
		fp.run_simple_switch()
	elif args.dumb_hub:
		fp.run_dumb_hub()
	elif args.topology:
		fp.do_topology_test()
	elif args.video_server:
		v = VideoServer()
		v.run()
	elif args.video_client:
		v = VideoClient()
		v.run()
	else:
		raise Exception("Don't really know what to do. Use --help switch for more information")


if __name__ == "__main__":
	main()
