import os
import time
from analyze import *
from matplotlib import pyplot as plt
import pandas as pd

import tcp_probe_work.parse_probe_result as tcppparser
import tcp_probe_work.ctrl_bpftrace as bpftracectrl
from experiments.exp1 import *


if __name__ == '__main__':
    for i in range(0,8):
        print(CUBIC_FIX_SWITCH_CMD.format(i))
        os.system(CUBIC_FIX_SWITCH_CMD.format(i))
        cubicandreno(bugfix=i,sub_folder=bugfixtostring(i))
        bpftracectrl.kill_bpf_trace_tcp_probe()