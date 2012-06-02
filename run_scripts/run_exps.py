#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNetConnections, custom
from mininet.link import TCLink
from mininet.node import CPULimitedHost
from time import sleep
import os
import socket
from mininet.cli import CLI
import random


#Ack division will ack each byte received. This caps the number of acks sent.
TCP_MAX_ACKS_DIV = 50

#Ack duplication sends each ack multiple times. This controls how many duplicates are sent.
TCP_NUM_DUP_ACKS = 100

#Enable this only if the number of acks is low. Otherwise tcpdump starts dropping a lot of packets
CAPTURE_ACKS = False


class MyTopo(Topo):
    "Simple two host topology"

    def __init__(self):
        Topo.__init__(self)
        receiver = self.add_host('receiver')
        sender = self.add_host('sender')
        self.add_link(sender, receiver)

def file_len(filename):
    with open(filename) as f:
        for i, l in enumerate(f):
            pass
        return i+1

def run_experiment( output = "sender.dump"):
    topo = MyTopo()
    host = custom(CPULimitedHost, cpu = .15)
    link = custom(TCLink, bw=1000, delay='100ms')

    net = Mininet(topo=topo, host=host, link=link)
    net.start()
    dumpNetConnections(net)
    net.pingAll()

    sender = net.getNodeByName('sender')
    receiver = net.getNodeByName('receiver')

    if CAPTURE_ACKS:
        sender.cmd("tcpdump -tt -nn 'tcp port 5001' &> %s &" % output)
    else:
        sender.cmd("tcpdump -tt -nn 'tcp dst port 5001' &> %s &" % output)
    sleep(1)


    # randomize address, because after a few repeats, the slow start is not observed anymore
    rand = str(random.randint(0,99)).zfill(2)
    receiver_IP = '1%s.11.0.2' % rand
    gateway_IP = '1%s.11.0.1' % rand


    receiver.cmd('../lwip/tcpsink -p 5001 -i %s -g %s &> receiver.out &' % (receiver_IP, gateway_IP))

    #make receiver forward packets from sender to internal tap interface
    receiver.cmd('sysctl net.ipv4.ip_forward=1')


    sender.cmd('sysctl net.core.netdev_max_backlog=500000')
    sender.cmd('sysctl net.ipv4.tcp_congestion_control=cubic')

    #add default route so that sender can sender to receiver's tap interface through the mininet link
    sender.cmd('route add default gw %s' % receiver.IP())

    #reduce MTU because otherwise the receive window is the limiting factor
    sender.cmd('ifconfig sender-eth0 mtu 200')

    print "starting transmission of data to %s" % receiver_IP
    sender.sendCmd('python sender.py --receiver=%s &> sender.out' % receiver_IP)


    print "waiting for transmission to complete"
    sender.waitOutput()

    print "killing tcpdump"
    sender.cmd('killall tcpdump')

    sleep(1)
    print "killing tcpsink"
    receiver.cmd("killall tcpsink")

    net.stop()


#first run
print "Running baseline experiment"
os.system("cd ../lwip && make clean && make && cd ../run_scripts")
run_experiment("sender.dump.baseline")
while(file_len("sender.dump.baseline") < 150):
    run_experiment("sender.dump.baseline")

#ack division
print "Running Ack Division experiment"
os.system("cd ../lwip && make clean && make EXTRA_FLAGS='-DTCP_ACK_DIV -DTCP_MAX_ACKS_DIV=%d' && cd ../run_scripts" % TCP_MAX_ACKS_DIV)
run_experiment("sender.dump.ack_division")
while(file_len("sender.dump.ack_division") < 150):
    run_experiment("sender.dump.ack_division")

#ack duplication
print "Running Ack duplication experiment"
os.system("cd ../lwip && make clean && make EXTRA_FLAGS='-DTCP_ACK_DUP -DTCP_NUM_DUP_ACKS=%d' && cd ../run_scripts" % TCP_NUM_DUP_ACKS )
run_experiment("sender.dump.ack_duplication")
while(file_len("sender.dump.ack_duplication") < 100):
    run_experiment("sender.dump.ack_duplication")
