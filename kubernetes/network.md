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

### IPERF problem (20-08-24)
<https://community.spiceworks.com/topic/724397-iperf-gigabit-bandwidth-test>
에서 우리와 비슷한 문제를 발견한 것 같았다.
<https://www.slashroot.in/iperf-how-test-network-speedperformancebandwidth>
를 보니, 

1. network throughput은 transfer rate of data from one place to another respect to time. 즉 한군데에서 다음으로 가는데 data의 transfer rate. Mbps(Mega bits per second)

2. TCP Window.
TCP는 transport layer protocol used for network communications. Send message and waits for acknowledgement.

Whenever two machines are communicating with each other, then each of them will inform the other about the
amount of bytes it is ready to receive at one time.
즉, maximum amount of data that a sender can send the other end, without an acknowledgement is called as Window Size.
이 TCP window size가 network throughput에 영향을 미치게 된다. 

결과창 해석

```
Interval:  Interval specifies the time duration for which the data is transferred.

Transfer: All data transferred using iperf is through memory, and is flushed out after completing the test. So there is no need to clear the transferred file after the test. This column shows the transferred data size.

Bandwidth: This shows the rate of speed with which the data is transferred.
```
```bash
# iperf -c 192.168.0.101 -t 20 -p 2000 -w 40k
-t   option used in the above command tells to transfer data for 20 seconds.

-p  will tell the client to connect the port 2000 on the server

-w will specify your desired window size value. As i told before, window size tuning will improve TCP transfer rate to a certain extent.
You can also tell the iperf client to show the transfer rate at an interval of 1 second, for the whole 10 second transfer, as shown below with -i option.
-i 1
-P 는 parallel TCP connection 몇개 만들건지.
-P 20

```
네트워크 bottleneck을 찾는 때에는 UDP가 훨씬 좋다. TCP는 window size도 matter되고, 
out of order delivery,(다 드롭시켜버리니까)
Network Jitter 
packet loss out of total number of packets. 
-b 100m 으로 100MBPS로 bandwith를 한정시킨다. -b 10G 이런식으로 full bandwith로 측정하는게 보통이겠지.
이러면 transfer, bandwith, network jitter, loast/total  값이 차례로 나오나봐. --debug 커맨드도 가능. 클라이언트쪽에서.

iperf3 -s -f m 와
iperf3 -c 192.168.0.17 -u -b 1000m
로 테스트해보니
[  5]   0.00-10.00  sec  1.11 GBytes   951 Mbits/sec  0.000 ms  0/820783 (0%)  sender
[  5]   0.00-10.00  sec  1.11 GBytes   951 Mbits/sec  0.010 ms  48/820782 (0.0058%)  receiver

가 나온다. 


```
kubectl exec -it pod이름 -- bin/sh
apt-get update
apt-get install iperf3
apt-get install net-tools

```

cppserver-1 은 10.244.1.7이란 IP쓰고있고, broadcast는 10.244.1.255 ether 주소는 (MAC은 unique하게 생성됨)
kube master nor hulkbuster has same MAC NIC.

iperf3 -c 192.168.0.17 -u -b 1000m

흠 일단 UDP로 하면 full bandwith 쓸 수 있는 것 같은데,
일단 NIC 로의 속도측정을 해보고 싶으니까.
이걸 어떻게 알수 있을지 찾아보자.

(END) 가 떠서 못 빠져나왔는데
실행취소키로 (ctrl+z) control Z control+z 로 탈출!


뒤에 interface 이름 넣으면 해당 NIC의 속도를 알 수 있다. 
```
sudo mii-tool -v enp2s0
sudo mii-tool -l enp2s0 하면
어떤 속도를 사용할지 알 수 있다.
1000base T-FD 라는건 full duplex 1Gbps 란느 것 같다.
<https://askubuntu.com/questions/1047542/why-does-ethernet-autonegotiation-selects-1000baset-hd-instead-of-1000baset-fd>

kubectl logs flannel-pod-이름 -n kubesystem 해서 로그를 봤어.

netstat -rn

하면 라우팅 테이블이보이고,

참고로 docker container 안에서 sshd를 살리고 root login을 허용하는 방법은 다음과 같습니다.

root@73b40d9d2a5b:/# apt-get install openssh-server

root@73b40d9d2a5b:/# vi /etc/ssh/sshd_config
#PermitRootLogin prohibit-password
PermitRootLogin yes

root@73b40d9d2a5b:/# /etc/init.d/ssh start

http://hwengineer.blogspot.com/2018/01/ppc64le-flannel-docker-container.html
```

일단 논문리딩하고오자


일단 UDP로 pod->native가 문제없는걸로봐서는
TCP 상의 문제인 것 같은데
<https://github.com/projectcalico/calico/issues/922>
에 따르면 encapsulation

