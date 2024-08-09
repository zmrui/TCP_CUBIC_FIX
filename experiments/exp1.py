import os
import time
from analyze import *
from matplotlib import pyplot as plt
import pandas as pd
import tcp_probe_work.parse_probe_result as tcppparser
import tcp_probe_work.ctrl_bpftrace as bpftracectrl


b0 = 0
b1 = 1
b2 = 2
b3 = 4
b1b2 = 3
b1b3 = 5 
b2b3 = 6
b1b2b3 = 7
CUBIC_FIX_SWITCH_CMD  = ''' sudo sh -c 'echo {} > /sys/module/tcp_cubic/parameters/bugfix' '''

def bugfixtostring(b:int):
    result = ""
    if b&4:
        result = "b3"+result   
    if b&2:
        result = "b2"+result 
    if b&1:
        result = "b1"+result
    if len(result) == 0:
        result = "b0"
    return result

def processdf(df):
    start_time = None
    for index, row in df.iterrows():
            if start_time is None:
                start_time = row['Dtime']
            Dtime0 = row['Dtime'] - start_time
            df.loc[index,'Dtime0'] = Dtime0
    df['Dtime0']=df['Dtime0'].astype(float)
    # print(df)
    result_df = df.copy()
    return result_df

def cubicandreno(bugfix,sub_folder,cca2='cubic',durition=5,keep=1,rtt=10,bw=100,loss=0,correlation=None,reorder_distance=None):
    
    os.system("dmesg -c > /dev/null")

    maxqsize= 1000
    print("maxqsize=",maxqsize)
    sub_folder_name = "results/8cwnd/0ms/"+sub_folder+"/"

    mn_net = mn_net_topo.mn_network(rtt=rtt,
                                    bw=bw,
                                    cca=cca2,
                                    reorderprobability=False,
                                    loss_probility=loss,
                                    maxqsize=maxqsize,
                                    correlation = correlation,
                                    reorder_distance = reorder_distance,
                                    sub_folder=sub_folder_name,
                                    nameprefix = "")
    
    mn_net.make_subfolder()
    bpftracectrl.start_bpf_trace_tcp_probe(toplevelpath=os.getcwd(),result_save_path=mn_net.workingdir)
    time.sleep(20)
    mn_net.start_mininet()
    # input("666666")
    mn_net.disable_tso()
    iptables_drop_string ='''iptables -A FORWARD -p tcp --dport 5201 -m statistic --mode nth --every 9999 --packet 11 -j DROP'''
    iptables_drop_string2 ='''iptables -A FORWARD -p tcp --dport 5202 -m statistic --mode nth --every 9999 --packet 11 -j DROP'''
    print(mn_net.h3.cmd(iptables_drop_string))
    print(mn_net.h3.cmd(iptables_drop_string2))
    # input()
    mn_net.receiver_iperf()
   
    mn_net.serder_iperf(count=80)

    mn_net.wait_until_iperf_end()
   
    mn_net.stop_mininet()
    bpftracectrl.kill_bpf_trace_tcp_probe()
    # time.sleep(10)
    tcppparser.removeipv6_and_change_time(mn_net.workingdir + "/tcp_probe.txtraw")
    renodf = tcppparser.parse_probe_text(filepath=mn_net.workingdir ,title="reno",sendercount=1,dest="10.0.0.2:5201")
    cubicdf = tcppparser.parse_probe_text(filepath=mn_net.workingdir,title="cubic",sendercount=2,dest="10.0.0.2:5202")
    renodf = renodf[renodf['datalength']>500][['Dtime', 'sequence', 'datalength','sndcwnd', 'sstresh', 'RTT_in_ms','srtt', 'ca_state' ]].copy()
    cubicdf = cubicdf[cubicdf['datalength']>500][['Dtime', 'sequence', 'datalength','sndcwnd', 'sstresh', 'RTT_in_ms','srtt', 'ca_state' ]].copy()
    plt.clf()   

    
    plt.plot(renodf['Dtime'].to_list(),renodf['sndcwnd'].to_list(),label="RENO CWND")
    plt.plot(cubicdf['Dtime'].to_list(),cubicdf['sndcwnd'].to_list(),label="CUBIC CWND")


    plt.xlabel("Time (milliseconds)")
    plt.ylabel("CWND")
    plt.title(sub_folder)
    # plt.xlim(130,380)
    # plt.ylim(0,24)
    plt.grid()
    plt.legend()
    plt.savefig(mn_net.workingdir+"/renocubic_fix{}.jpg".format(sub_folder))

    plt.clf()
    renodf2 = processdf(renodf)
    cubicdf2 = processdf(cubicdf)
    plt.plot(renodf2['Dtime0'].to_list(),renodf['sndcwnd'].to_list(),label="RENO CWND")
    plt.plot(cubicdf2['Dtime0'].to_list(),cubicdf['sndcwnd'].to_list(),label="CUBIC CWND")
    plt.xlabel("Time (milliseconds)")
    plt.ylabel("CWND")
    plt.title(sub_folder)
    # plt.xlim(130,380)
    # plt.ylim(0,24)
    plt.grid()
    plt.legend()
    plt.savefig(mn_net.workingdir+"/start0_renocubic_fix{}.jpg".format(sub_folder))

    os.system("dmesg > {}/printk.txt".format(mn_net.workingdir))
