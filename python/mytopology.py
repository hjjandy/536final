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

Ex_seconds = 120
Mo_seconds = Ex_seconds + 20

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
	def expIDs(self):
		return range(0, self.N)

class LineSwitchTopo(MyTopo):
	def __init__(self, n=7, **opts):
		MyTopo.__init__(self, n, **opts)
		hosts = self.hs
		switches = self.ss
		for x in range(0, n-1):
			self.addLink(switches[x], switches[x+1], bw=100, delay='10ms', loss=2)
	def expIDs(self):
		return [0, 1, 2, 3] #N=7
			
class StarSwitchTopo(MyTopo):
	def __init__(self, n=7, **opts):
		MyTopo.__init__(self, n, **opts)
		hosts = self.hs
		switches = self.ss
		for x in range(1, n):
			self.addLink(switches[0], switches[x], bw=100, delay='10ms', loss=2)
	def expIDs(self):
		return [0, 1]

class TreeSwitchTopo(MyTopo):
	def __init__(self, n=7, **opts):
		MyTopo.__init__(self, n, **opts)
		hosts = self.hs
		switches = self.ss
		for x in range(0, 3):
			self.addLink(switches[x], switches[2*x+1], bw=100, delay='10ms', loss=2)
			self.addLink(switches[x], switches[2*x+2], bw=100, delay='10ms', loss=2)
	def expIDs(self):
		return [0, 1, 3] # make sure self.N = 7
		
class RingSwitchTopo(MyTopo):
	def __init__(self, n=7, **opts):
		MyTopo.__init__(self, n, **opts)
		hosts = self.hs
		switches = self.ss
		for x in range(0, n):
			self.addLink(switches[x], switches[(x+1)%n], bw=100, delay='10ms', loss=2)
	def maxExpIdx(self):
		return [0]

class MeshSwitchTopo(MyTopo):
	def __init__(self, n=7, **opts):
		MyTopo.__init__(self, n, **opts)
		hosts = self.hs
		switches = self.ss
		for x in range(0, n):
			for y in range(x+1, n):
				self.addLink(switches[x], switches[y], bw=100, delay='10ms', loss=2)
	def expIDs(self):
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
		for iter in range(0, 10):
			for sID in topo_instance.expIDs():
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

if __name__ == '__main__':
	setLogLevel( 'info' )
	#all_topos = {'LineTopology': LineSwitchTopo(7), 'RingTopology': RingSwitchTopo(7), 'StarTopology': StarSwitchTopo(7), 'TreeTopology': TreeSwitchTopo(7), 'MeshTopology': MeshSwitchTopo(7)}
	all_topos = {'LineTopology': LineSwitchTopo(7), 'StarTopology': StarSwitchTopo(7), 'TreeTopology': TreeSwitchTopo(7)}
	#all_topos = {'StarTopology': StarSwitchTopo(7), 'TreeTopology': TreeSwitchTopo(7)}
	for name in all_topos:
		my_test(name, all_topos[name])
	#test()
