# [More experiment results](more_results.md)

# tcp_cubic_fix

This patch fixes some CUBIC bugs so that  “CUBIC achieves at least the same throughput as Reno in small-BDP networks” [rfc9438](https://www.rfc-editor.org/rfc/rfc9438.html). 
It consists of three bug fixes, all changing function bictcp_update() of tcp_cubic.c, which controls how fast CUBIC increases its congestion window size snd_cwnd. 


# Bug fix 1:


```patch
---
 net/ipv4/tcp_cubic.c | 14 +++++++++-----
 1 file changed, 9 insertions(+), 5 deletions(-)

diff --git a/net/ipv4/tcp_cubic.c b/net/ipv4/tcp_cubic.c
index 5dbed91c6178..6789ebdaa615 100644
--- a/net/ipv4/tcp_cubic.c
+++ b/net/ipv4/tcp_cubic.c
@@ -219,7 +219,7 @@ static inline void bictcp_update(struct bictcp *ca, u32 cwnd, u32 acked)
 	ca->ack_cnt += acked;	/* count the number of ACKed packets */
 
 	if (ca->last_cwnd == cwnd &&
-	    (s32)(tcp_jiffies32 - ca->last_time) <= HZ / 32)
+	    (s32)(tcp_jiffies32 - ca->last_time) <= min(HZ / 32, usecs_to_jiffies (ca->delay_min)))
 		return;
```

The original code bypasses bictcp_update() under certain conditions to reduce the CPU overhead. Intuitively, when last_cwnd==cwnd, bictcp_update() is executed 32 times per second. As a result, it is possible that bictcp_update() is not executed for several RTTs when RTT is short (specifically < 1/32 second = 31 ms), thus leading to low throughput in these RTTs.

The patched code executes bictcp_update() 32 times per second if RTT > 31 ms or every RTT if RTT < 31 ms, when last_cwnd==cwnd. 

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

The original code follows RFC 8312 (obsoleted CUBIC RFC).

The patched code follows RFC 9438 (new CUBIC RFC).

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

The original code calculates tcp_cwnd using the current estimated RENO snd_cwnd.

The patched code calculates tcp_cwnd using the estimated RENO snd_cwnd after one RTT, because tcp_cwnd is used to increase snd_cwnd for the next RTT.

# Experiments:

 

Below are Mininet experiments to demonstrate the performance difference between the original CUBIC and patched CUBIC.

 

Network: link capacity = 100Mbps, RTT = 4ms

TCP flows: one RENO and one CUBIC. initial cwnd = 10 packets. the first data packet of each flow is lost

 
cwnd of RENO and original CUBIC flows

![cwnd of RENO and original CUBIC](https://raw.githubusercontent.com/zmrui/tcp_cubic_fix/main/results/Initial%2010%20CWND/First%20group%20RTT%204ms/b0/renocubic_fixb0.jpg)

 

cwnd of RENO and patched CUBIC (with bug fixes 1, 2, and 3) flows.

![Snd_cwnd of RENO and patched CUBIC](https://raw.githubusercontent.com/zmrui/tcp_cubic_fix/main/results/Initial%2010%20CWND/First%20group%20RTT%204ms/b1b2b3/renocubic_fixb1b2b3.jpg)

 

The result of patched CUBIC with different combinations of bug fixes 1, 2, and 3 can be found at the following link, where you can also find more experiment results.  

[More experiment results](more_results.md)
