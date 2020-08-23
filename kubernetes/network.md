#### 2020-08-23

iperf3 -s -f m 이라 함은 서버를 여는거야 5201포트로  포맷은 mb. G로하면 기가바이트인가봐

iperf3 -c 192.168.0.6 -f m 이라 함은 서버를 접속해서 해당 ip와 비교.

근데 hulk에서 서버 열고 kubernetes에서 보내면 
0.00-10.04  sec  1.09 GBytes   937 Mbits/sec                  receiver
0.00-10.00  sec  1.09 GBytes   940 Mbits/sec    0             sender

반면 kubernetes에서 서버 열고 hulk에서 보내면 
0.00-10.01  sec   927 MBytes   777 Mbits/sec                  receiver 
 0.00-10.00  sec   929 MBytes   779 Mbits/sec    0             sender
 
 이모양인데 cpu차이일까? 

```
iperf3 -s -p 5101
iperf3 -s -p 5102
iperf3 -s -p 5103
```
이런식으로 포트를 다르게 열수도있다.
<https://github.com/esnet/iperf/issues/408>
40G 네트워크를 충분히 사용안하는 이슈가 있다.
iperf3 -c hostname -T s1 -p 5101 &; iperf3 -c hostname -T s2 -p 5102 &; iperf3 -c hostname -T s3 -p 5103 &;

```
iperf3 parallel stream performance is much less than iperf2. Why?
iperf3 is single threaded, and iperf2 is multi-threaded. We recommend using iperf2 for parallel streams. If you want to use multiple iperf3 streams use the method described here.
```
