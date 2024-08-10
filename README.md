# Experiments:

Below are Mininet experiments to demonstrate the performance difference between the original CUBIC and patched CUBIC.

## Topology and setup

- Topology
![Topology](https://raw.githubusercontent.com/zmrui/tcp_cubic_fix/main/isoflow-export-2024-08-10T15_55_23.611Z.png)

- Disable TSO on all nodes
- Drop the first data packet of each flow using the iptables rule
- Packet drop rule execute on the middle router
- Reno and CUBIC traffic: IPerf3
- CWND information captured the kprobe:__ip_local_out function on the sender node using [bpftrace](https://github.com/bpftrace/bpftrace)

## 1. Network: link capacity = 100Mbps, RTT = 4ms, Initial cwnd = 10 packets

TCP flows: one RENO and one CUBIC. The first data packet of each flow is lost

- Cwnd of RENO and original CUBIC flows

![cwnd of RENO and original CUBIC](https://raw.githubusercontent.com/zmrui/tcp_cubic_fix/main/results/Initial%2010%20CWND/First%20group%20RTT%204ms/b0/renocubic_fixb0.jpg)


- Cwnd of RENO and patched CUBIC (with bug fixes 1, 2, and 3) flows.

![Snd_cwnd of RENO and patched CUBIC](https://raw.githubusercontent.com/zmrui/tcp_cubic_fix/main/results/Initial%2010%20CWND/First%20group%20RTT%204ms/b1b2b3/renocubic_fixb1b2b3.jpg)

 
- More combinations of bug fixes 1, 2, and 3

[Fix bug 0](https://github.com/zmrui/tcp_cubic_fix/blob/main/results/Initial%2010%20CWND/First%20group%20RTT%204ms/b0/renocubic_fixb0.jpg),
[Fix bug 1](https://github.com/zmrui/tcp_cubic_fix/blob/main/results/Initial%2010%20CWND/First%20group%20RTT%204ms/b1/renocubic_fixb1.jpg),
[Fix bug 2](https://github.com/zmrui/tcp_cubic_fix/blob/main/results/Initial%2010%20CWND/First%20group%20RTT%204ms/b2/renocubic_fixb2.jpg),
[Fix bug 3](https://github.com/zmrui/tcp_cubic_fix/blob/main/results/Initial%2010%20CWND/First%20group%20RTT%204ms/b3/renocubic_fixb3.jpg)

[Fix bug 1 and 2](https://github.com/zmrui/tcp_cubic_fix/blob/main/results/Initial%2010%20CWND/First%20group%20RTT%204ms/b1b2/renocubic_fixb1b2.jpg),
[Fix bug 1 and 3](https://github.com/zmrui/tcp_cubic_fix/blob/main/results/Initial%2010%20CWND/First%20group%20RTT%204ms/b1b3/renocubic_fixb1b3.jpg),
[Fix bug 2 and 3](https://github.com/zmrui/tcp_cubic_fix/blob/main/results/Initial%2010%20CWND/First%20group%20RTT%204ms/b2b3/renocubic_fixb2b3.jpg),
[Fix bug 1 and 2 and 3](https://github.com/zmrui/tcp_cubic_fix/blob/main/results/Initial%2010%20CWND/First%20group%20RTT%204ms/b1b2b3/renocubic_fixb1b2b3.jpg)

## 2. Network: link capacity = 100Mbps, RTT = 0ms, Initial cwnd = 10 packets

### Combinations of bug fixes 1, 2, and 3

[Fix bug 0](https://github.com/zmrui/tcp_cubic_fix/tree/main/results/Initial%2010%20CWND/Second%20group%20RTT%200ms/b0/renocubic_fixb0.jpg), 
[Fix bug 1](https://github.com/zmrui/tcp_cubic_fix/tree/main/results/Initial%2010%20CWND/Second%20group%20RTT%200ms/b1/renocubic_fixb1.jpg), 
[Fix bug 2](https://github.com/zmrui/tcp_cubic_fix/tree/main/results/Initial%2010%20CWND/Second%20group%20RTT%200ms/b2/renocubic_fixb2.jpg), 
[Fix bug 3](https://github.com/zmrui/tcp_cubic_fix/tree/main/results/Initial%2010%20CWND/Second%20group%20RTT%200ms/b3/renocubic_fixb3.jpg)

[Fix bug 1 and 2](https://github.com/zmrui/tcp_cubic_fix/tree/main/results/Initial%2010%20CWND/Second%20group%20RTT%200ms/b1b2/renocubic_fixb1b2.jpg), 
[Fix bug 1 and 3](https://github.com/zmrui/tcp_cubic_fix/tree/main/results/Initial%2010%20CWND/Second%20group%20RTT%200ms/b1b3/renocubic_fixb1b3.jpg), 
[Fix bug 2 and 3](https://github.com/zmrui/tcp_cubic_fix/tree/main/results/Initial%2010%20CWND/Second%20group%20RTT%200ms/b2b3/renocubic_fixb2b3.jpg), 
[Fix bug 1 and 2 and 3](https://github.com/zmrui/tcp_cubic_fix/tree/main/results/Initial%2010%20CWND/Second%20group%20RTT%200ms/b1b2b3/renocubic_fixb1b2b3.jpg)

## 3 Network: link capacity = 100Mbps, RTT = 4ms, Initial cwnd = 8 packets

### Combinations of bug fixes 1, 2, and 3

[Fix bug 0](https://github.com/zmrui/tcp_cubic_fix/tree/main/results/Initial%208%20CWND/First%20group%20RTT%204ms/b0/renocubic_fixb0.jpg), 
[Fix bug 1](https://github.com/zmrui/tcp_cubic_fix/tree/main/results/Initial%208%20CWND/First%20group%20RTT%204ms/b1/renocubic_fixb1.jpg), 
[Fix bug 2](https://github.com/zmrui/tcp_cubic_fix/tree/main/results/Initial%208%20CWND/First%20group%20RTT%204ms/b2/renocubic_fixb2.jpg), 
[Fix bug 3](https://github.com/zmrui/tcp_cubic_fix/tree/main/results/Initial%208%20CWND/First%20group%20RTT%204ms/b3/renocubic_fixb3.jpg)

[Fix bug 1 and 2](https://github.com/zmrui/tcp_cubic_fix/tree/main/results/Initial%208%20CWND/First%20group%20RTT%204ms/b1b2/renocubic_fixb1b2.jpg), 
[Fix bug 1 and 3](https://github.com/zmrui/tcp_cubic_fix/tree/main/results/Initial%208%20CWND/First%20group%20RTT%204ms/b1b3/renocubic_fixb1b3.jpg), 
[Fix bug 2 and 3](https://github.com/zmrui/tcp_cubic_fix/tree/main/results/Initial%208%20CWND/First%20group%20RTT%204ms/b2b3/renocubic_fixb2b3.jpg), 
[Fix bug 1 and 2 and 3](https://github.com/zmrui/tcp_cubic_fix/tree/main/results/Initial%208%20CWND/First%20group%20RTT%204ms/b1b2b3/renocubic_fixb1b2b3.jpg)

## 4 Network: link capacity = 100Mbps, RTT = 0ms, Initial cwnd = 8 packets

### Combinations of bug fixes 1, 2, and 3

[Fix bug 0](https://github.com/zmrui/tcp_cubic_fix/tree/main/results/Initial%208%20CWND/Second%20group%20RTT%200ms/b0/renocubic_fixb0.jpg), 
[Fix bug 1](https://github.com/zmrui/tcp_cubic_fix/tree/main/results/Initial%208%20CWND/Second%20group%20RTT%200ms/b1/renocubic_fixb1.jpg), 
[Fix bug 2](https://github.com/zmrui/tcp_cubic_fix/tree/main/results/Initial%208%20CWND/Second%20group%20RTT%200ms/b2/renocubic_fixb2.jpg), 
[Fix bug 3](https://github.com/zmrui/tcp_cubic_fix/tree/main/results/Initial%208%20CWND/Second%20group%20RTT%200ms/b3/renocubic_fixb3.jpg)

[Fix bug 1 and 2](https://github.com/zmrui/tcp_cubic_fix/tree/main/results/Initial%208%20CWND/Second%20group%20RTT%200ms/b1b2/renocubic_fixb1b2.jpg), 
[Fix bug 1 and 3](https://github.com/zmrui/tcp_cubic_fix/tree/main/results/Initial%208%20CWND/Second%20group%20RTT%200ms/b1b3/renocubic_fixb1b3.jpg), 
[Fix bug 2 and 3](https://github.com/zmrui/tcp_cubic_fix/tree/main/results/Initial%208%20CWND/Second%20group%20RTT%200ms/b2b3/renocubic_fixb2b3.jpg), 
[Fix bug 1 and 2 and 3](https://github.com/zmrui/tcp_cubic_fix/tree/main/results/Initial%208%20CWND/Second%20group%20RTT%200ms/b1b2b3/renocubic_fixb1b2b3.jpg)
