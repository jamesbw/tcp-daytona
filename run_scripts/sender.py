#! /usr/bin/python

import socket
import datetime
import os
import argparse


def millis_since(start):
	secs = (datetime.datetime.now() - start).seconds
	micros = (datetime.datetime.now() - start).microseconds
	return secs * 1000 + micros / 1000

def send(HOST):

	PORT = 5001
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print "Connecting to ", HOST, "port", PORT
	s.connect((HOST, PORT))
	print "Connected to", HOST


	payload = "".join(['a']*4096)

	start = datetime.datetime.now()

	#saturate the sender buffer for a while
	while  millis_since(start)  < 1300:
		s.send(payload)

	s.close()

	print "Finished sending after %d millis" % millis_since(start)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Sender script")
	parser.add_argument("--receiver", '-r', help="Receiver IP", required=True)

	args=parser.parse_args()
	send(args.receiver)