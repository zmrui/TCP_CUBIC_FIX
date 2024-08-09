import pandas as pd
from decimal import Decimal

def comp_time(time1:str,time2:str):
    '20:19:03.971179'
    '20:19:08.984640'
    t1_list=time1.split(":")
    t1h=Decimal(t1_list[0])
    t1m=Decimal(t1_list[1])+t1h*60
    t1s=Decimal(t1_list[2])+t1m*60
    try:
        t2_list=time2.split(":")
        t2h=Decimal(int(t2_list[0]))
        t2m=Decimal(int(t2_list[1]))+t2h*60
        t2s=Decimal(t2_list[2])+t2m*60
    except:
        print(time2)
        print(t2_list)
        exit()

    return (t2s - t1s)

def removeipv6_and_change_time(tcp_probe_text_file_path):
    reveisedfile = []
    # start_time = None
    
    with open (tcp_probe_text_file_path, 'r') as fin:
        lines  = fin.readlines()
        for line in lines:
            templine = line.replace("::ffff:",'')
            # old_time_field = templine.split(',')[0]

            # if start_time is None:
            #     start_time = old_time_field
            # Dtime = comp_time(start_time, old_time_field)
            # new_time_field = str(Dtime)
            
            # templine = templine.replace(old_time_field,new_time_field)

            reveisedfile.append(templine)

    with open(tcp_probe_text_file_path.replace("raw",''),'w') as fout:
        fout.writelines(reveisedfile)

def parse_probe_text(filepath,title,sendercount,dest:str):
    columns = ['time', 'source', 'destination', 'datalength', 'sequence', 'acknumber', 'sndcwnd', 'sstresh', 'srtt' ,'rcvwnd','ca_state']
    with open(filepath + "/tcp_probe.txt", 'r') as f:
        lines = f.readlines()

    lines2 = []
    for line in lines:
        if dest in line:
            lines2.append(line.replace("::ffff:",""))

    data = [line.strip().split(',') for line in lines2]
    df = pd.DataFrame(data, columns=columns)

    start_time =None
    df['destination']=df['destination'].astype(str)
    for index, row in df.iterrows():
        if dest == row['destination']:
            if start_time is None:
                start_time = row['time']
            Dtime = comp_time(start_time,row['time'] )
            rtt_in_millisecond = (int(row['srtt']) >> 3) / 1000
            df.loc[index,'Dtime'] = Dtime*1000
            df.loc[index,'RTT_in_ms'] = rtt_in_millisecond

    df['Dtime']=df['Dtime'].astype(float)
    df['time']=df['time'].astype(str)
    df['source']=df['source'].astype(str)
    df['destination']=df['destination'].astype(str)
    df['datalength']=df['datalength'].astype(int)
    df['sequence']=df['sequence'].astype(int)
    df['acknumber']=df['acknumber'].astype(int)
    df['sndcwnd']=df['sndcwnd'].astype(int)
    df['sstresh']=df['sstresh'].astype(int)
    df['srtt']=df['srtt'].astype(int)
    df['RTT_in_ms']=df['RTT_in_ms'].astype(float)
    df['rcvwnd']=df['rcvwnd'].astype(int)
    df['ca_state']=df['ca_state'].astype(int)

    sender_df = df[dest == df['destination']][['Dtime', 'sequence', 'datalength','sndcwnd', 'sstresh', 'RTT_in_ms','srtt', 'ca_state' ]].copy()
    # sender_df = sender_df[sender_df['datalength']>500][['Dtime', 'sequence', 'datalength','sndcwnd', 'sstresh', 'RTT_in_ms','srtt', 'ca_state' ]].copy()
    
    sender_df.reset_index(drop=True)

    sender_df.to_csv(filepath+"/"+title+"_sender%d_df.csv"%sendercount)
    # print(sender_df)
    return sender_df


if __name__ == '__main__':
    # parse_probe_text("result.txt",dest="10.0.0.2:5201")
    # print(comp_time('20:19:03.971179', '20:19:08.984640'))

    removeipv6_and_change_time('/home/lisong-20/G-CCAs/4-Mininet/results/fairness/fifo_Dumbell_40mbit_50ms_349pkts_Noneloss_2flows_3tcpbuf_bbr/run0/tcp_probe.txt')