from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel, info
from mininet.cli import CLI
import os
import time
from decimal import *
import analyze 


class ReorderLossTopo( Topo ):
    def build( self, rtt, bw, reorderprobability, lossprob, correlation,reorder_distance,maxq):

        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')

        if reorderprobability:
            reorder_string="reorder %f%%%% %d%%%%"%(reorderprobability, correlation)
        else:
            reorder_string=None
        if reorder_distance:
            lnkdelay = reorder_distance
        else:
            lnkdelay = 1

        self.addLink(h1,h3,
                   bw=1000,jitter=reorder_string, loss=lossprob,max_queue_size=50000)
        self.addLink(h2,h3,
                   bw=bw,loss=0,max_queue_size=maxq)


#start_mininet
#Finished
#set rtt, bandwidth, congestion control algorithm
class mn_network:
    def __init__(self,rtt=int,
                 bw=int,
                 cca=str,
                 maxqsize=int,
                 sub_folder=None,
                 loss_probility=None,
                 reorderprobability=None,
                 correlation=None,
                 reorder_distance=None,
                 nameprefix="") -> None:
        
        self.rtt=rtt
        self.bw=bw
        self.cca=cca
        self.reorder=reorderprobability
        self.reorder_tc_prob = None

        self.probability=reorderprobability
        # 25 == 25% delay
        
        if self.probability:
            self.reorder_tc_prob = 100.0 - self.probability
        # 25 == 25% send immedtly and 75% delay

        self.correlation=correlation
        self.reorder_distance=reorder_distance
        self.packet_drop_position_list=None
        self.packet_reorder_position_list=None
        self.maxqsize=maxqsize
        self.loss_probility = loss_probility
        self.name=nameprefix+cca+"_"+str(rtt)+"ms_"+str(bw)+"Mbps"
        self.top_folder=os.getcwd()
        self.sub_folder=None
        if sub_folder:
            self.sub_folder= os.path.join(self.top_folder,sub_folder) 


        self.iperf_start_time = None
        self.iperf_expected_end_time = None

        self.CWND_start = 90
        self.tso_enabled = True

        FILE_PATH = "/proc/kmsg"
        self.kmsg_file = open(FILE_PATH,"r")
        print("@","rtt="+str(rtt)+"ms","bw="+str(bw)+"Mbps","cca="+cca)
        self.startTime = time.time()

        self.focus_begin = 0
        self.focus_end = 0

    def make_subfolder(self):
        if self.sub_folder:
            if not os.path.exists(self.sub_folder):
                os.makedirs(self.sub_folder)
        
        self.workingdir = os.path.join(os.getcwd(),self.sub_folder)
        print("Working Dir:",self.workingdir) 
            
    def start_mininet(self):

        topo = ReorderLossTopo(rtt=self.rtt,
                               bw=self.bw, 
                               lossprob=self.loss_probility, 
                               reorderprobability = self.reorder_tc_prob,
                               correlation=self.correlation,
                               reorder_distance = self.reorder_distance, 
                               maxq = self.maxqsize)

        net = Mininet( topo=topo,
                    host=CPULimitedHost, link=TCLink, #xterms=True,
                    autoStaticArp=True )    

        net.start()
        h1, h2, h3 = net.getNodeByName('h1', 'h2', 'h3')

        h1eth0 = h1.intf("h1-eth0")
        h1eth0.setIP("192.168.0.1/24")
        h1.cmd("route add -net 10.0.0.0/24 dev h1-eth0 gw 192.168.0.3")

        h2eth0 = h2.intf("h2-eth0")
        h2eth0.setIP("10.0.0.2/24")
        h2.cmd("route add -net 192.168.0.0/24 dev h2-eth0 gw 10.0.0.3")


        h3eth0 = h3.intf("h3-eth0")
        h3eth0.setIP("192.168.0.3/24")
        h3eth1 = h3.intf("h3-eth1")
        h3eth1.setIP("10.0.0.3/24")

        # if not "bpf" in self.cca:
        #     h1.cmd("sysctl -w net.ipv4.tcp_congestion_control=%s"%(self.cca))
        h1.cmd("sysctl -p")
        h3.cmd("sysctl -p")
        
        print("@ start mininet: %s"%(time.time()-self.startTime))
        self.net=net
        self.h1=h1
        self.h2=h2
        self.h3=h3
        return net,h1,h2,h3

    def stop_mininet(self):
        print("@ stop mininet")
        with open(os.path.join(self.workingdir,self.name+'_name.txt'),'w') as f:
            f.write(self.name)
        self.net.stop()

    def receiver_iperf(self,port1=5201,port2=5202):
        receiver_iperflogpath = os.path.join(self.workingdir,"r1.json")
        if os.path.isfile(receiver_iperflogpath):
            os.remove(receiver_iperflogpath)
        self.h2.cmd("iperf3 -s -p %d -i 1 --json --logfile %s -1 &"%(port1,receiver_iperflogpath))

        receiver_iperflogpath = os.path.join(self.workingdir,"r2.json")
        if os.path.isfile(receiver_iperflogpath):
            os.remove(receiver_iperflogpath)
        self.h2.cmd("iperf3 -s -p %d -i 1 --json --logfile %s -1 &"%(port2,receiver_iperflogpath))

        

    def serder_iperf(self,cca1='reno',cca2='cubic',count=100,port1=5201,port2=5202):
        self.durition_time = 10
        self.iperf_start_time = time.time()
        self.iperf_expected_end_time = self.iperf_start_time + self.durition_time
        
        sender_iperflogpath1 = os.path.join(self.workingdir,"s1.json")
        if os.path.isfile(sender_iperflogpath1):
            os.remove(sender_iperflogpath1)
        
        sender_iperflogpath = os.path.join(self.workingdir,"s2.json")
        if os.path.isfile(sender_iperflogpath):
            os.remove(sender_iperflogpath)
        
        h1cmd ="iperf3 -c 10.0.0.2 -p %d --congestion %s -k %d -f m -i 1 --json --logfile %s &"%(port1,cca1,count,sender_iperflogpath1)
        self.h1.cmd(h1cmd)
        h1cmd2="iperf3 -c 10.0.0.2 -p %d --congestion %s -k %d -f m -i 1 --json --logfile %s &"%(port2,cca2,count,sender_iperflogpath)
        self.h1.cmd(h1cmd2)

    

    def disable_tso(self):
        self.tso_enabled = False
        print(self.h1.cmd("ethtool -K h1-eth0 tx off sg off tso off gso off"),end='')
        print(self.h2.cmd("ethtool -K h2-eth0 tx off sg off tso off gso off"),end='')
        print(self.h3.cmd("ethtool -K h3-eth0 tx off sg off tso off gso off"),end='')
        print(self.h3.cmd("ethtool -K h3-eth1 tx off sg off tso off gso off"),end='')
        # print(self.h3.cmd("wireshark &"))
        
    def wait_until_iperf_end(self):
        print("@ wait until iperf ends...")
        while(True):
            if time.time() < self.iperf_expected_end_time:
                time.sleep(5)
            else:
                print("@ iperf end...:%s"%(time.time()-self.startTime))
                # self.h1.cmd("mv %s %s"%(self.iperflogpath, self.name+"_iperflog"))
                # self.iperflogpath=self.name+"_iperflog"
                return