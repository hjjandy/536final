#!/usr/bin/python
from mininet.log import setLogLevel
from mininet.node import UserSwitch, OVSKernelSwitch  # , KernelSwitch
from mininet.cli import CLI
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.node import CPULimitedHost
from mininet.util import pmonitor
from signal import SIGINT
from time import time
import os
import math
import time

Ex_seconds = 120
Mo_seconds = Ex_seconds + 20

class SingleSwitchTopo(Topo):
	#Build the topology here.
	#We built a simple star topology for this assignment.
	#If you want to build other interesting topologies
	#   such as a tree, fat-tree, or jelly-fish, it can be done here.
	#Single switch connected to 4 hosts.
	def __init__(self, n=4, **opts):
		Topo.__init__(self, **opts)
		BottomClient = self.addHost('hb')
		LeftClient = self.addHost('hl')
		RightClient = self.addHost('hr')
		TopClient = self.addHost('ht')
		switchServer = self.addSwitch('s0')
		#default Configuration
		self.addLink(LeftClient, switchServer, bw=100)
		self.addLink(RightClient, switchServer, bw=100)
		self.addLink(TopClient, switchServer, bw=100)
		self.addLink(BottomClient, switchServer, bw=100)
def test():
	os.system('mn -c')
	os.system('sysctl -w net.ipv4.tcp_congestion_control=reno')
	#You can add os.system code here
	#Note that the configuration in this python script will affect your mininet.
	#Therefore, please make sure that you restore the configuration to the default values.
	switches = {  # 'reference kernel': KernelSwitch,
				  #'reference user': UserSwitch,
				  'Open vSwitch kernel': OVSKernelSwitch }
	for name in switches:
		switch = switches[ name ]
		topo = SingleSwitchTopo(0)
		network = Mininet(topo=topo, host=CPULimitedHost, link=TCLink, switch = switch)
		network.start()
		#Initialize the Network
		#If you want to use the command line interface, use CLI(network).
		#Details of the CLI are at:
		#   http://mininet.org/walkthrough/#part-3-mininet-command-line-interface-cli-commands
		#You can use popen features as done below.
		#Details of popen are at:
		#   https://docs.python.org/2/library/subprocess.html
		popens = {}
		hosts=network.hosts
		switches=network.switches
		#popens[(hosts[1], 'server')] = hosts[1].popen('iperf -s')
		#popens[(hosts[2], 'client')] = hosts[2].popen('iperf -c {} -t {}'
		#							.format(hosts[1].IP(), str(Ex_seconds)))
		for h in hosts:
			popens[(h, 'server')] = h.popen('iperf -s')
		for hc in hosts:
			for hs in hosts:
				if hc.name != hs.name:
					popens[(hc, 'client')] = hc.popen('iperf -c {} -t {}'.format(hs.IP(), str(Ex_seconds)))
		print 'Monitoring output for', Mo_seconds, 'seconds'
		endTime = time() + Mo_seconds
		for h, line in pmonitor(popens, timeoutms=500):
			if h:
				print '%s %s: %s' % (h[0].name, h[1], line)
			if time() >= endTime:
				for p in popens.values():
					p.send_signal(SIGINT)
		network.stop()

class MyTopo(Topo):
	def __init__(self, n=7, **opts):
		Topo.__init__(self, **opts)
		self.N = n
		self.hs = dict() #hosts
		self.ss = dict() #switches
		for x in range(0, n):
			self.hs[x] = self.addHost('h{}'.format(x))
			self.ss[x] = self.addSwitch('s{}'.format(x))
			self.addLink(self.hs[x], self.ss[x], bw=100, delay='10ms', loss=2)
	def maxExpIds(self):
		return range(0, self.N)

class LineSwitchTopo(MyTopo):
	def __init__(self, n=7, **opts):
		MyTopo.__init__(self, n, **opts)
		hosts = self.hs
		switches = self.ss
		for x in range(0, n-1):
			self.addLink(switches[x], switches[x+1], bw=100, delay='10ms', loss=2)
	def maxExpIds(self):
		return [0, 1, 2, 3] #N=7
			
class StarSwitchTopo(MyTopo):
	def __init__(self, n=7, **opts):
		MyTopo.__init__(self, n, **opts)
		hosts = dict()
		switches = dict()
		for x in range(1, n):
			self.addLink(switches[0], switches[x], bw=100, delay='10ms', loss=2)
	def maxExpIds(self):
		return [0, 1]

class TreeSwitchTopo(MyTopo):
	def __init__(self, n=7, **opts):
		MyTopo.__init__(self, n, **opts)
		hosts = dict()
		switches = dict()
		for x in range(0, 3):
			self.addLink(switches[x], switches[2*x+1], bw=100, delay='10ms', loss=2)
			self.addLink(switches[x], switches[2*x+2], bw=100, delay='10ms', loss=2)
	def maxExpIds(self):
		return [0, 1, 3] # make sure self.N = 7
		
class RingSwitchTopo(MyTopo):
	def __init__(self, n=7, **opts):
		MyTopo.__init__(self, n, **opts)
		hosts = dict()
		switches = dict()
		for x in range(0, n):
			self.addLink(switches[x], switches[(x+1)%n], bw=100, delay='10ms', loss=2)
	def maxExpIdx(self):
		return [0]

class MeshSwitchTopo(MyTopo):
	def __init__(self, n=7, **opts):
		MyTopo.__init__(self, n, **opts)
		hosts = dict()
		switches = dict()
		for x in range(0, n):
			for y in range(x+1, n):
				self.addLink(switches[x], switches[y], bw=100, delay='10ms', loss=2)
	def maxExpIds(self):
		return [0]

def my_test(topo_name, topo_instance):
	os.system('mn -c')
	os.system('sysctl -w net.ipv4.tcp_congestion_control=reno')
	#You can add os.system code here
	#Note that the configuration in this python script will affect your mininet.
	#Therefore, please make sure that you restore the configuration to the default values.
	switches = {  # 'reference kernel': KernelSwitch,
				  #'reference user': UserSwitch,
				  'Open vSwitch kernel': OVSKernelSwitch }
	for name in switches:
		switch = switches[name]
		# 10 runs for each topology
		for iter in range(0, 1):
			for sID in topo_instance.maxExpIds():
				sName = 'h%d' % sID
				fname = '%s-%02d-%s' % (topo_name, (iter+1), sName)
				fobj = open(fname, 'w')
				#fobj.write('*+#@$-*+#@$-*+#@$-*+#@$-*+#@$-*+#@$-*+#@$-*+#@$-\n')
				fobj.write('@Test for topology "%s" begins:\n' % topo_name)
				fobj.write('\n>>Iteration %d<<\n' % (iter+1))
				#topo = SingleSwitchTopo(0)
				network = Mininet(topo=topo_instance, host=CPULimitedHost, link=TCLink, switch=switch)
				network.start()
				popens = {}
				hosts=network.hosts
				switches=network.switches
				for hs in hosts:
					if sName == hs.name:
						popens[(hs, 'server')] = hs.popen('iperf -s')
						for hc in hosts:
							if hc.name != hs.name:
								popens[(hc, 'client')] = hc.popen('iperf -c {} -t {}'.format(hs.IP(), str(Ex_seconds)))
								print 'Client %s -> Server %s' % (hc.name, hs.name)
						break #only one server
				fobj.write('Monitoring output for %d seconds\n' % Mo_seconds)
				endTime = time() + Mo_seconds
				for h, line in pmonitor(popens, timeoutms=500):
					if h:
						fobj.write( '%s %s: %s' % (h[0].name, h[1], line))
					if time() >= endTime:
						for p in popens.values():
							p.send_signal(SIGINT)
				network.stop()
				fobj.write('\n@Test for topology "%s" ends.\n' % topo_name)
				fobj.close()
				time.sleep(2) # sleep 2 seconds

if __name__ == '__main__':
	setLogLevel( 'info' )
	#all_topos = {'LineTopology': LineSwitchTopo(7), 'RingTopology': RingSwitchTopo(7), 'StarTopology': StarSwitchTopo(7), 'TreeTopology': TreeSwitchTopo(7), 'MeshTopology': MeshSwitchTopo(7)}
	#all_topos = {'LineTopology': LineSwitchTopo(7), 'StarTopology': StarSwitchTopo(7), 'TreeTopology': TreeSwitchTopo(7)}
	all_topos = {'LineTopology': LineSwitchTopo(7)}
	for name in all_topos:
		my_test(name, all_topos[name])
	#test()
