# [More experiment results](more_results.md)

# tcp_cubic_fix

This page is the details for Linux TCP CUBIC patch declaration 

This patch fixes some CUBIC bugs so that  “CUBIC achieves at least the same throughput as Reno in small-BDP networks” [rfc9438](https://www.rfc-editor.org/rfc/rfc9438.html). 
It consists of three bug fixes, all changing function bictcp_update() of tcp_cubic.c, which controls how fast CUBIC increases its congestion window size.


# Bug fix 1:


```patch
diff --git a/net/ipv4/tcp_cubic.c b/net/ipv4/tcp_cubic.c
index 5dbed91c6178..6bfca2b51b39 100644
--- a/net/ipv4/tcp_cubic.c
+++ b/net/ipv4/tcp_cubic.c
@@ -219,7 +219,7 @@ static inline void bictcp_update(struct bictcp *ca, u32 cwnd, u32 acked)
 	ca->ack_cnt += acked;	/* count the number of ACKed packets */
 
 	if (ca->last_cwnd == cwnd &&
-	    (s32)(tcp_jiffies32 - ca->last_time) <= HZ / 32)
+	    (s32)(tcp_jiffies32 - ca->last_time) < min(HZ / 32, usecs_to_jiffies (ca->delay_min)))
 		return;
```

The original code bypasses bictcp_update() under certain conditions to reduce the CPU overhead. Intuitively, when last_cwnd==cwnd, bictcp_update() is executed no more than 32 times per second. 
As a result, it is possible that bictcp_update() is not executed for several RTTs when RTT is short (specifically < 1/32 second = 31 ms), thus leading to low throughput in these RTTs.

The patched code executes bictcp_update() at least once per RTT .

# Bug fix 2:

 
```patch
@@ -301,14 +301,18 @@ static inline void bictcp_update(struct bictcp *ca, u32 cwnd, u32 acked)
 	if (tcp_friendliness) {
 		u32 scale = beta_scale;
 
-		delta = (cwnd * scale) >> 3;
+		if (cwnd < ca->bic_origin_point)
+			delta = (cwnd * scale) >> 3;
+		else
+			delta = cwnd;
 		while (ca->ack_cnt > delta) {		/* update tcp cwnd */
 			ca->ack_cnt -= delta;
 			ca->tcp_cwnd++;
 		}
```

The original code calculates the delta according to RFC 8312 (obsoleted CUBIC RFC).

The patched code calculates the delta according to RFC 9438 (new CUBIC RFC).

```
Once _W_est_ has grown to reach the _cwnd_ at the time of most
recently setting _ssthresh_ -- that is, _W_est_ >= _cwnd_prior_ --
the sender SHOULD set α__cubic_ to 1 to ensure that it can achieve
the same congestion window increment rate as Reno, which uses AIMD(1,
0.5).
```


# Bug fix 3:

 
```patch
-
-		if (ca->tcp_cwnd > cwnd) {	/* if bic is slower than tcp */
-			delta = ca->tcp_cwnd - cwnd;
+		
+		u32 tcp_cwnd_next_rtt = ca->tcp_cwnd + (ca->ack_cnt+cwnd)/delta;
+		if (tcp_cwnd_next_rtt > cwnd) {  /* if bic is slower than tcp */
+			delta = tcp_cwnd_next_rtt - cwnd;
 			max_cnt = cwnd / delta;
 			if (ca->cnt > max_cnt)
 				ca->cnt = max_cnt;
```

The original code calculates tcp_cwnd as the current estimated RENO cwnd.

The patched code calculates tcp_cwnd as the estimated RENO cwnd after one RTT, because tcp_cwnd is used to   


# Mininet experiment

A Mininet experiment to demonstrate the performance difference of original CUBIC and patched CUBIC.

 
Network: link capacity = 100Mbps, RTT = 4ms, initial cwnd = 10 packets.

Two flows: one RENO and one CUBIC, the first data packet of each flow is lost


CWND in following figures: print out snd_cwnd at every time when ip_local_out() was called


1. Snd_cwnd of RENO and original CUBIC

![Snd_cwnd of RENO and original CUBIC](https://raw.githubusercontent.com/zmrui/tcp_cubic_fix/main/results/Initial%2010%20CWND/First%20group%20RTT%204ms/b0/renocubic_fixb0.jpg)

2. Snd_cwnd of RENO and patched CUBIC (with bug fixes 1, 2, and 3).

![Snd_cwnd of RENO and patched CUBIC](https://raw.githubusercontent.com/zmrui/tcp_cubic_fix/main/results/Initial%2010%20CWND/First%20group%20RTT%204ms/b1b2b3/renocubic_fixb1b2b3.jpg)


 
## Reproduce using Mininet Scripts

Link to [Github Repo](https://github.com/zmrui/tcp_cubic_fix)

This script relys on bpftrace to listen on kprobe:__ip_local_out function to print out snd_cwnd information for each tcp packets.

Steps:

1. Install bpftool

```
https://github.com/libbpf/bpftool
```

2. Install Mininet

```
https://github.com/mininet/mininet
```

3. Get bpftrace
```
wget https://github.com/bpftrace/bpftrace/releases/download/v0.21.2/bpftrace -O tcp_probe_work/bpftrace.o
```

4. Configuration

Config Link Delay at `analyze/mn_net_topo.py` at line 31 and line 33

Config output path at `experiments/exp1.py` at line 50

5. Start

Start the script from in sudo permission(Required by Mininet) in the root folder 
`sudo python3 start.py`

# [More experiment results](more_results.md)
