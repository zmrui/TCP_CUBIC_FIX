import subprocess
import os
import time
from decimal import Decimal
bpf_traace_tcp_probe_cmd = "exec %s/bpftrace.o %s/ip_local_out.bt -q -f text > %s/tcp_probe.txtraw"
bpf_trace_process = None
def start_bpf_trace_tcp_probe(toplevelpath,result_save_path:str):
    global bpf_trace_process
    fileobj = os.path.join(toplevelpath,'tcp_probe_work')
    bpf_traace_actual_cmd = bpf_traace_tcp_probe_cmd%(fileobj,fileobj,result_save_path)
    bpf_trace_process = subprocess.Popen(bpf_traace_actual_cmd,shell=True)
    print('[bpf_traace_actual_cmd] ',bpf_traace_actual_cmd)

def kill_bpf_trace_tcp_probe():
    global bpf_trace_process
    if bpf_trace_process:
        print("KILL bpf_trace_process")
        bpf_trace_process.kill()
    bpf_trace_process = None


if __name__ == '__main__':
    # start_bpf_trace_tcp_probe(result_save_path=os.path.join(os.getcwd(),"result.txt"))
    # time.sleep(20)
    # kill_bpf_trace_tcp_probe()
    pass