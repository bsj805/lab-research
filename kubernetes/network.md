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


2020-08-26 

오늘 드디어 어느정도 이유를 찾은 것 같다.
<https://bugs.launchpad.net/plainbox-provider-checkbox/+bug/1584112>
pod에서 -A 8,8 option으로 실행시키면 정상적으로 (쿠버네티스 네트워크.pptx 페이지 13) 
bandwidth가 나온다.

```
iperf3 -c 10.0.0.3 -T s1 -p 5101 & iperf3 -c 10.0.0.3 -T s2 -p 5102 & iperf3 -c 10.0.0.3 -T s3 -p 5103
```

서버를 세개열고 이걸로해보라고하더라.(<https://github.com/esnet/iperf/issues/408>)
일단 native-native사이에는
3.13 3.14 3.14 gbits/sec 이나오는데,

9.52 gbits/sec이나오네.

pod -native사이에
(black위 pod - white native 10.0.0.3)
3.23 3.13 2.90  -> 6.36+ 2.90 = 9.26? 
일단 근데 갑자기 retransmission이 많아지면서 아까와같은결과가 안나오긴하네

일단 차이점은 receiver측 cpu utilization이 엄청나게 증가했다?

native -native (10G)
42.2 3.9 (receiver 즉 서버쪽이 white인경우) white의 cpu 3.9퍼래

잘 안나올때:
20.9 50.6 (white cpu 50.6%쓴다함) ret:5120
33.2  6.1  ret:4690
34.7  24.1 ret:2773
33.3  12.4 ret:4693
33.1   33.1  ret:4521

udp -b 5000m -A 8,8 -V

했을때
1.64gbits/sec 
99.9% 49.1% 

iperf3 -c 10.0.0.3 -A 4,4 -V
로 뒀을때
5.36gbits/sec

33.6 16.2 ret:3646

iperf3 -c 10.0.0.3 -A 8,8 -V 로 했을때
9.34gbits/sec
40.9 26.7 ret:20

9.35gbits/sec
40.4  4.3  ret:30

```
root@cpp-1-6f4f57c9f9-ch9td:/# while true;do iperf3 -c 10.0.0.3 -A 8,8 -V; done;
```
로 했는데 kubectl top pods로 하니 400m정도밖에 소모 안하는 것 같음 (cpu를) 

9.37 gbits/sec
43.3   4.8  ret:21

9.34 gbits/sec
40.7  53.6  ret:39

9.38gbits/sec
40.4    53.4  ret:16

9.38gbits/sec
41.4    53.6  ret:40

9.37gbits/sec

43.0  53.6  ret:51

9.38gbits/sec  

43.7  53.6 ret:17

9.37gbits/sec

42.3 53.2 ret:18

9.37 gbits/sec

40.2 53.9 ret:10

단순히 cpu number에 따라 결정되는 것 같다.
어떤 cpu에서 실행되느냐의 문제인 것 같은데.

일단 oprofile 설치

```
sudo apt-get install oprofile
```
nmon이라는 툴이 더좋네 ㅎ
https://linuxhint.com/oprofile-tutorial/
로 oprofile을 배워서 실제로 어디서 cpu를 쓰는지 보자.
[강성민] [오후 5:45] sudo iptables -nL
[강성민] [오후 5:45] 여기서 체인 리스트를 볼 수 있고
[강성민] [오후 5:45] 보니까 저 nf_conntrack이 가득 차면 패킷을 드랍한다고 하는데 iptables로 notrack 옵션을 주는건 트래킹을 안 한다는 모양이에요
라는 듯?

다 /proc/net/에 있었다. nf_contrack?


2020/08/31

kubectl describe pods calico-node-9sx2w -n calico-system 
를 통해서 보니,
BGP가 not 활설화되어 있어서 179번 포트를 모두 열어주었다 (양쪽모두) 
sudo iptables -A OUTPUT -p tcp --dport 179 -j ACCEPT
```
black@black-Z10PA-U8-Series:~$ cat /proc/modules | grep nf_conntrack
     │nf_conntrack_netlink 45056 0 - Live 0x0000000000000000
         │nfnetlink 16384 4 ip_set,nf_conntrack_netlink, Live 0x0000000000000000
  │nf_conntrack 139264 6 xt_nat,ip_vs,xt_conntrack,xt_MASQUERADE,nf_conntrack_netlink,nf_nat, Live 0x0000000000000000
       │nf_defrag_ipv6 24576 2 ip_vs,nf_conntrack, Live 0x0000000000000000
      │nf_defrag_ipv4 16384 1 nf_conntrack, Live 0x0000000000000000
     │libcrc32c 16384 3 ip_vs,nf_nat,nf_conntrack, Live 0x0000000000000000

```

```
이걸로 네트워크 
sudo ifconfig ens4f1 10.0.0.3 netmask 255.255.255.0 up
```
pod쪽에서
```
iperf3 -c 10.0.0.3 -A8 -R 로 해봤는데 이걸 operf를 돌릴 수 있었어 su - 를 통해서. 그랬더니 operf를 쓰니까 4번cpu가 추가로 돌아가네. 
```

<https://bugs.launchpad.net/ubuntu/+source/linux/+bug/1836816>

를보면 nf_conntrack에서 race가 일어난다고 하는 것 같음

UDP가 connectionless니까, conntrack entry는 packet is first sent일 때까지 생성되지 않아.
UDP packet이 같은 시간에 같은 소켓으로 다만 다른 쓰레드에서 보내진다면,
1. 어떤 packet도 confirmed conntrack entry 를 찾지 못해서, 같은 tuple임에도 불구하고 2개의 conntrack entry가 생기게 함 
(각각의 쓰레드가 각각 등록)
2.  다른 패킷이 get_unique_tuple()을 호출 하기 전에 conntrack entry가 하나의 패킷에 대해 confirmed 되었어. 즉 각각의 패킷이 다른 reply를 받아
source port가 changed 되었는데

__nf_conntrack_confirm()을 부를 때 패킷이 드랍되어 버려. confirm conntrack entries 해야 할때. 

<https://stackoverflow.com/questions/31546835/tcp-receiving-window-size-higher-than-net-core-rmem-max/35438236>

그래 결국은 window size에 limit이 걸려있으니 full bandwidth를 쓰지 못하는게 아니냐.

```
sudo sysctl -a | grep net 이거하면 
```

net.ipv4.tcp_rmem=4096    131072 6291456  -> maximum receiver window size가 6 MiB라는 것을 알 수 있다. 
TCP는 tends to allocate twice the requested size. 그러니 max receiver window size는 3 MiB가 되어야 하는 것이 맞다.

Note that TCP actually allocates twice the size of the buffer requested in the setsockopt(2) call, and so a succeeding getsockopt(2) call will not return the same size of buffer as requested in the setsockopt(2) call. TCP uses the extra space for administrative purposes and internal kernel structures, and the /proc file values reflect the larger sizes compared to the actual TCP windows.

(man tcp 하면 나오는 것)

그런데 net.core.rmem_max = 212992 
을 보면 maximum receiver window size가 208 KiB를 넘을 수 없음을 알려준다. 
according to man tcp:

tcp_rmem max: the maximum size of the receive buffer used by each TCP socket. This value does not override the global net.core.rmem_max. This is not used to limit the size of the receive buffer declared using SO_RCVBUF on a socket.

in void tcp_select_initial_window()

```
if (wscale_ok) {
    /* Set window scaling on max possible window
     * See RFC1323 for an explanation of the limit to 14
     */
    space = max_t(u32, sysctl_tcp_rmem[2], sysctl_rmem_max);
    space = min_t(u32, space, *window_clamp);
    while (space > 65535 && (*rcv_wscale) < 14) {
        space >>= 1;
        (*rcv_wscale)++;
    }
}
```
https://blog.cloudflare.com/how-to-achieve-low-latency/

IP 에 conntrack이 관여하지않게 하는 방법이 써있는거같다.
http://www.iorchard.net/2017/05/20/k8s_dns_perf_problem.html
여기를 보면 대강 그 이유를 알 수 있는 듯 하다.

즉슨, SNAT는 
(소스 IP, 소스 포트, 목적 IP, 목적 포트)와 같이 unique tuple들로 정의된다. 이 4개의 element가 하나라도 다르면 다른 entry가 된다.

 컨테이너에서 나가는 패킷은 SNAT를 통하는데 저 소스 포트는 docker0가 만들어내는 포트들일 것이다. 이 포트가 계속 달라지기 때문에 
 SNAT table이 꽉찬다는 것이 아닐까? conntrack table이 SNAT 정보를 저장하기 위해 만들어진다.
 
 <https://www.slideshare.net/lorispack/docker-networking-101> 아예 ethernet을 내 NIC를 사용하게 하는 방법도 있다.
 
 ```
 sudo iptables -nvL -t nat
 ```
 nat 정보확인
 
 맨 위 PREROUTING에서 docker0 로 오는 모든 패킷이 SNAT 됨을 알 수 있다.
 SNAT라 함은 source의 IP를 바꾸는 NAT방식을 말한다. <https://www.joinc.co.kr/w/Site/System_management/NAT>
 처음에 네트워크 를 public IP로 바꿔야할 때에 패킷 헤더의 source IP를 우리의 public IP로 바꿈으로써 인터넷은 아 이게 어디서 온 거구나
 하면서 연결할 수 있고 반대로 들어올 때에는 DNAT. desitnation을 바꾸는 거겠지. 
 <https://brownbears.tistory.com/151>
 
 지금 저거 해서 postrouting chain에 적혀있는게 SNAT한다는 거.  172.17.0.0/16 짜리에 대해서 알아서 IP 할당해서 처리하도록 되어있다.
 
 
 
