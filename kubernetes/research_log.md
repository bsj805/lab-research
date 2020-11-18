## 우수학부생 연구학점제




### 2020.09.05

첫번째 미팅

우선, kubernetes 상에서 발생하는 문제라 cni가 관여하지 않는가에 대한 생각이 들었다
-> 문제 단순화해서, 

![image](https://user-images.githubusercontent.com/47310668/92705840-fdf7c300-f38e-11ea-8f7c-32ee60272771.png)

여기서 docker 0만 있는 상태에서 
pod-native간 상태는 어떠한가?

라고 봤을때 여전히 같은 문제가 발생했다.

즉, kubernetes 상에서만 발생하는 문제는 아닐수 도 있다는 생각이 든다.

-> 지금 operf로 해서 나왔던 nf_conntrack은 정말 nat때문에 발생하는 문제일 수도 있다는 생각.
<https://linuxstory1.tistory.com/entry/iptables-%EA%B8%B0%EB%B3%B8-%EB%AA%85%EB%A0%B9%EC%96%B4-%EB%B0%8F-%EC%98%B5%EC%85%98-%EB%AA%85%EB%A0%B9%EC%96%B4>
```bash
iptables --list-rule
```
로 보니까 
![image](https://user-images.githubusercontent.com/47310668/92706719-b6256b80-f38f-11ea-8334-270f144075a4.png)
이런게 있어서.
흠 

forward 룰을 보다보면, 어떤식으로 패킷을 받는것인지 알 수 있지 않을까 싶었다.

### 2020-09-10

![image](https://user-images.githubusercontent.com/47310668/92706625-a27a0500-f38f-11ea-8f6a-a93ea1bc98e0.png)

-A FORWARD -j DOCKER-USER  # append, forward룰,  https://qastack.kr/server/245711/iptables-tips-tricks 에 따르면 그냥 interface를 define하는 것이라한다.
-A FORWARD -j DOCKER-ISOLATION-STAGE- 
-A FORWARD -o docker0 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT  패킷이 docker0를 통해서 나갈 때, conntrack이라는 모듈 (connectiont tracking extension == conntrack)을 사용하라는 명령.
ctstate는 conntrack의 일부. related 라 함은, 기존 연결에 속하지만, 새로운 연결을 요청하는 패킷, established는 기존 연결의 일부인 패킷. iptables의 연결 추적 기능! 
이걸 포워딩하겠다는 것은,  docker0에서 나갈 때 기존 연결과 관련된 패킷만 forward하겠다. 
-A FORWARD -o docker0 -j DOCKER    docker 0 를 통해서 나가는 패킷은, DOCKER라는 룰로 점프해라?  DOCKER룰은 docker0로 들어오는 모든 패킷을 return 시키라는데?
-A FORWARD -i docker0 ! -o docker0 -j ACCEPT  docker0를 통해서 들어오는 패킷은 docker0로 나간 것이 아니던 맞던 포워딩해주면된다. 
-A FORWARD -i docker0 -o docker0 -j ACCEPT 
-A FORWARD -s 10.244.0.0/16 -j ACCEPT  //flannel 송신자
-A FORWARD -d 10.244.0.0/16 -j ACCEPT // flannel 수신자
-A OUTPUT -m conntrack --ctstate NEW -m comment --comment "kubernetes service portals" -j KUBE-SERVICES
-A OUTPUT -j KUBE-FIREWALL
-A DOCKER-ISOLATION-STAGE-1 -i docker0 ! -o docker0 -j DOCKER-ISOLATION-STAGE-2  docker0로 들어오는 패킷이 아닌데 docker0로 나간 패킷이면 DOCKER_ISOLATION_STAGE 2로 가라.
-A DOCKER-ISOLATION-STAGE-1 -j RETURN   아니면 리턴~
-A DOCKER-ISOLATION-STAGE-2 -o docker0 -j DROP  // docker0로 나간패킷은 드랍~
-A DOCKER-ISOLATION-STAGE-2 -j RETURN
-A DOCKER-USER -j RETURN


https://ssup2.github.io/theory_analysis/Linux_conntrack/
에 따르면
-A FORWARD -o docker0 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT

는 docker0에서 포워드 되려는 패킷이 connection tracking helper에 의해 예상된 새로운 connection을 생성하려는 상태거나 현재 존재하는 커넥션을
통해 통신하려는 경우 허용하는 rule을 명령어로 정하고 있다.

iptable에서 nat rule을 설정하면 이와 반대되는 reverse NAT는 iptable에 reverse Nat rule이 없어도 자동으로 수행된다.
이 conntrack Module의 커넥션정보를 바탕으로 암묵적으로 reverse NAT를 수행하기 때문!
![image](https://user-images.githubusercontent.com/47310668/92718069-39e55500-f39c-11ea-80e2-4212a56a8047.png)
아마 이거가 나오는 걸 보니
저패킷이 저렇게 바뀌는 것이아닐까?


sudo conntrack -L --src -nat 하면 source NAT connection을 보이는 것이라고 한다.
```
sudo iptables -nvL -t nat
```

Chain OUTPUT (policy ACCEPT 36 packets, 2248 bytes)                                                                                                                                          
 pkts bytes target     prot opt in     out     source               destination                                                                                                              
 797K   49M KUBE-SERVICES  all  --  *      *       0.0.0.0/0            0.0.0.0/0            /* kubernetes service portals */
 158K 9460K DOCKER     all  --  *      *       0.0.0.0/0           !127.0.0.0/8          ADDRTYPE match dst-type LOCAL

이건 패킷이 나갈때 의 룰인건데, (OUTPUT)
<https://stackoverflow.com/questions/26963362/dockers-nat-table-output-chain-rule>
127.x.x.x 로 시작하지 않는 IP address 로 가는 패킷들은 handed over to target (DOCKER 체인) for further processing


Chain PREROUTING (policy ACCEPT 1 packets, 102 bytes)                                                                                                                                        
 pkts bytes target     prot opt in     out     source               destination                                                                                                              
1336K   63M KUBE-SERVICES  all  --  *      *       0.0.0.0/0            0.0.0.0/0            /* kubernetes service portals */
 154K 9448K DOCKER     all  --  *      *       0.0.0.0/0            0.0.0.0/0            ADDRTYPE match dst-type LOCAL 
 
 prerouting도 모든패킷올때 docker chain으로보내기 인듯.
 
 봐봐.. 
 Chain POSTROUTING (policy ACCEPT 36 packets, 2248 bytes)                                                                                                                                     
 pkts bytes target     prot opt in     out     source               destination                                                                                                              
1968K  102M KUBE-POSTR  all  --  *      *       0.0.0.0/0            0.0.0.0/0            /* kubernetes postrouting rules */
 2240  135K MASQUERADE  all  --  *      !docker0  172.17.0.0/16        0.0.0.0/0 
 
 지금 postrouting에서 docker0가 아닌 interface로 나가는 패킷은 마스커레이딩을 당해.
 즉슨, docker0로 가는 패킷은 source ip가 저거여도되는데 (docker 0가 172.17.0.1 이거든)
 근데 다른 인터페이스에서 ex) ens4f1에서 패킷이 나가는데 172.17.0.0/16 이면 안된다 이거야. 이때 NAT가 들어가는거지.
 이게 POSTROUTING rule.
 
 <https://gist.github.com/nerdalert/a1687ae4da1cc44a437d> POSTROUTING이 뭐냐고? 이거야!
 
 
 자 이렇게 
 ![image](https://user-images.githubusercontent.com/47310668/92722785-12de5180-f3a3-11ea-9395-4b168cf9cf6e.png)

어떻게 docker network가 작동하는 지 알아보았습니다!

이제 

iperf3 의 core affinity가 어떻게 동작하는지

각 코어에서 어떤 프로세스가 일어나는건지 알아볼 수있는 툴이 있는지! top, ps

또 반복해서 실험했을 때 특정코어는 항상 10G가 나오는 지 뭐 이런 거도 알아봐야한다!
```

sudo docker run -it bruzn/ubuntu-cppthreadserver300 bin/bash 로 실행했다.
```
apt-get update
apt-get install net-tools
apt-get install iperf3

tcpdump -c 30 -i ens4f1 -n 해야지 name으로안나온다. -A였나?
sudo tcpdump -c 30 -i ens4f1 -n port 5201 으로 해 보통.
```
Set the CPU affinity for the sender (-A 2) or the sender, receiver (-A 2,3), where the cores are numbered starting at 0. This has the same effect as running numactl -C 4 iperf3.
```
core affinity는
numactl -C 4 iperf3  를 하는 것과 똑같다고한다.(<https://support.cumulusnetworks.com/hc/en-us/articles/216509388-Throughput-Testing-and-Troubleshooting#cpu_affinity>)

```
man numactl
numactl --physcpubind=+0-4,8-12 myapplic arguments Run myapplic on cpus 0-4 and 8-12 of the current cpuset.
Only execute process on cpus.  This accepts cpu numbers as shown in the processor fields of /proc/cpuinfo, or relative cpus as in relative to the current cpuset.  You may
              specify "all", which means all cpus in the current cpuset.  Physical cpus may be specified as N,N,N or  N-N or N,N-N or  N-N,N-N and  so  forth.   Relative  cpus  may  be
              specifed  as  +N,N,N or  +N-N or +N,N-N and so forth. The + indicates that the cpu numbers are relative to the process' set of allowed cpus in its current cpuset.  A !N-N
              notation indicates the inverse of N-N, in other words all cpus except N-N.  If used with + notation, specify !+N-N.

```
-C cpus 
라고 한다.


<https://stackoverflow.com/questions/14720332/numactl-physcpubind>

top을 키고, f로 lastusedcpu항목을 키고보니까

실제로 iperf3 -c 10.0.0.3 -A2 를 하면 cpu를 2번만 사용한 것 처럼 표시된다.
networkmanager라는 프로세스가 계속 자리를 바꿔서 2.6%정도를 차지하는데 그게 nmon에서 
그렇게 표시되는걸지도 모른다.
그래 사실 numactl 

아니면 gvfs라는 프로세스도 보이고
tmux:server도 갑자기 차지를 많이하다가도, nmon의 부정확성일지도 모른다. ksoftirqd/8 ? 라는것도  보인다.

이 ksoftirqd/0~9는 각 cpu에서만 돌아간다 즉 ksoftirqd/0은 0번코어에서만 돌아가는 애인거다. 
http://egloos.zum.com/rousalome/v/9978671

우리의 컴퓨터는 연결된 device와 IRQs (interrupt requests)들을 통해 통신한다. device에서 interrupt가 오면,
operating system pauses what it was doing and starts addressing that interrupt. 즉 인터럽트 관리를 시작한다.
어떤 경우에는 IRQ가 너무 빠르게 와서 다른 IRQ가 오기전에 OS가 그 이전의 IRQ를 처리하지 못하는 경우가 생긴다. 
이것은 high speed network card 가 receives a very large number of packets in a short time frame일 때 벌어질 수 있다.

OS가 IRQ들을 제때제때 handle하지 못하면 ( 다음 IRQ가 너무빨리 도착하기 때문) OS는 그들의 processing을 special internal process named
ksoftirqd에게 맡겨버린다.

흠
확실히 native-native하면 ksoftirqd가 적고 pod-native하면 ksoftirqd가 많이 일어나.
<https://qastack.kr/ubuntu/7858/why-is-ksoftirqd-0-process-using-all-of-my-cpu> 여기에 CPU 어떻게 하면 설정할 수 있는지에
대해서도 나오는 것 같다. 

<https://qastack.kr/ubuntu/7858/why-is-ksoftirqd-0-process-using-all-of-my-cpu>

```
cat /proc/interrupts
```
interrupt개수보는법. <https://forums.gentoo.org/viewtopic-t-1102698-start-0.html> <- 왜 ksoftirqd 가 network에 영향을 미치고 있는지.

6번코어에서도는애들은
cpuhp/6
idle_inject/6
migration/6
ksoftirqd/6
kworker/6:0H-kb+
khugepaged
kblockd
kwapd0
irq/31-pciehp
scsi_eh_1
scsi_eh_7
systemd-udevd
loop0
loop5
loop9
nvidia-modeset/
networkd-dispat
polkitd
probing-thread
containerd (7
dockerd *3

gdbus
gvfs-udisks2-vo
docker-proxy
containerd-shim
pager
docker

coredns
flanneld
flanneld
etcd


무조건 한 코어는 그만한 속도를 내는 cpu가 있다 분명히.
sudo ps -A -o pid,psr,comm,cpuid >> process.txt
(<https://stackoverflow.com/questions/5732192/ps-utility-in-linux-procps-how-to-check-which-cpu-is-used> 참고)
로 어떤 코어에서 돌리는 지 볼수있는데 (어떤 프로세스가 어떤 코어에서 도는지) 

일단 
![image](https://user-images.githubusercontent.com/47310668/92740595-d289ce00-f3b8-11ea-998a-4ac48ff12707.png)
이중 하나랑 같은 코어에서 돌아가니까 그런게 아닐까?

먼저 (sd-pam)은 systemd --user 의 child인건데, 

일단 iperf3 -A 옵션은 -P 랑같이 사용하면 무용지물이야.
-P는 여러쓰레드를만들어서 available core에 할당하게 되니까.

vi /proc/cpuinfo 하면 cpu정보들보인다.

numactl의 cpu affinity가 어떻게 작동하는지 -> (<https://stackoverflow.com/questions/14720332/numactl-physcpubind>)

일단 첫번째 의심은

gvfs-udisks2-vo 가 같은 코어에서 돌아가면, 속도가 안나온다? 
일단 얘가 없어 10G가 나오는 애들은.
coredns도 없네

kworker 는 placeholder process for 커널 worker threads./ kernel을 위한 대부분의 프로세싱을 담당한다.
especially in cases where there are interrupts, timers, I/O , etc.
system cpu time의 대부분을 차지한다. 

kworker/0:1 은 내 첫번째 core의 process이고
kworker/1:1 은 내 두번째 core의 프로세스이고~

load를 겪을때, kworker때문에라면, echo l > /proc/sysrq-trigger을 이용해서 뭐 로그를만들고하라는데
<https://askubuntu.com/questions/33640/kworker-what-is-it-and-why-is-it-hogging-so-much-cpu>


### 2020 -09- 14

회의
도커 네트워크 구성에 관한 ppt
iptables의 ip masqurade
iperf - CPU Affinity
작업할 코어 지정하는 형식으로 동작하는 게 맞음
ksoftirqd가 여러개 생겨서 코어마다 CPU를 사용하는 게 있음
이건 커널 단에서 쓰레드를 코어에 할당해주는 거고, 인터럽트 -> 호출 하는 쓰레드
이 ksoftirqd가 ~10G가 나올 때는 생성되지 않는 것으로 보아, ~10G가 나오지 않고 해당 CPU가 먹고 있을 때는 인터럽트 처리가 원활히 이루어지지 않았다는 것을 의미함.
해당 부분에 대한 커널 소프트웨어 리퀘스트 데몬에 대해서 조금 자세히 살펴볼 것
-> 다음 주 중으로 랩에서 미팅

ksoftirqd의 역할 알아오기 
tcpdump bandwidth 안좋을 때와 좋을 때 찍어보기
iperf3 MSS 로 packet 사이즈 다르게 해서 찾아보기

### 2020-09-15
softirqd가 생기는 이유는 원래 
<https://www.usenix.org/system/files/nsdi19-zhuo.pdf>
![image](https://user-images.githubusercontent.com/47310668/93546486-cf38a880-f99d-11ea-9bf0-0c82c1220c1e.png)
이런식으로 네트워크 스택을 두번 타고 가야되는데, 
컨테이너에서 출발한 패킷은
처음에 virtual ip src :port  dst ip :port ( kernel overlay network stack)

였다가

OS kernel 이 eth 헤더를 붙여서 실제 패킷처럼 만들어.

eth | virtual ip src :port  dst ip :port

그러고 virtual switch는 dst ip 를 읽어서 라우팅 테이블을 참고해 physical ip와 port ㅎ헤더를 붙여줘
phy src ip:port dst ip:port |eth | virtual ip src :port  dst ip :port

그러면 이건 UDP 패킷과 UDP payload같을 거야. 

즉 이렇게 패킷을 바꾸는데 인터럽트가 발생하고, 
![image](https://user-images.githubusercontent.com/47310668/93547162-5c303180-f99f-11ea-8532-d97b2935a0e8.png)
<https://d2.naver.com/helloworld/47667>
이제 linux 나 unix 같이 POSIX 계열은 소켓을 fd 형태로 어플리케이션에 노출해. 
커널소켓은 send socket buffer가 있고, receive socket buffer가 있어.
소켓마다 TCB (TCP control Block) , TCP 연결에 처리하는데 필요한 정보를 담아놔. TCB에 있는 데이터는 connection state(LISTEN, ESTABLISHED, TIME_WAIT 등), receive window, congestion window, sequence 번호, 재전송 타이머 등이다.
패킷생성을 할 때, TCP 패킷이 가장먼저 만들어지지.
TCP segment. 
checksum, payload (최대길이는 receive window, congestion window, MSS(maximum segment size) 중 최댓값), 그리고 checksum 계산한다.
checksum 계산시 IP 주소들, segment 길이등이 포함된다.

이제 이렇게 TCP segment를 IP 레이어로 이동하는데, TCP segment에 IP 헤더를 추가하고, IP routing 즉 목적지 IP 주소로 가기 위한 다음 장비의 IP 주소찾기를 한다.
그다음은 ethernet layer이다.

ETHERNET에선 ARP로 next hop ip 였던 곳의 MAC주소를 찾아. 그리고 Ethernet 헤더를 패킷에 추가한다.
그럼 라우팅 할때마다 ethernet 헤더가 벗겨지고 IP 헤더가 벗겨지고 다시 씌워지겠지

패킷을 받을때는, 
![image](https://user-images.githubusercontent.com/47310668/93547570-4c651d00-f9a0-11ea-89f4-81ba4f46655f.png)
이것과 같다.
1.NIC가 패킷을 메모리에 기록하고, CRC로 패킷이 올바른지 검사하고, 호스트의 메모리 버퍼로 전송한다.
2.버퍼는 NIC 드라이버가 커널에 요청해서 미리 패킷 수신용으로 할당한 메모리고, 할당받은 후에 드라이버는 NIC에 메모리 주소와 크기를 알려준다.
3.만약 NIC가 패킷을 받았는데 할당된 메모리가 없으면 NIC가 패킷을 drop 시킨다.

4.패킷을 호스트메모리로 전송시키면 NIC가 호스트 OS에 인터럽트를 보낸다. 
5.드라이버가 새로운 패킷을 보고 자신이 처리하는 패킷인지 검사.
6.드라이버가 상위 레이어로 패킷을 전달하려면, 운영체제가 사용하는 패킷 구조체로 포장해야한다.
linux의 sk_buff (아 이게 skb네) 가 운영체제의 패킷구조체이다. 드라이버가 이렇게 포장한 패킷을 상위 레이어로 전달한다. 

7.ethernet layer에서도 패킷이 올바른지 검사하고, 상위 네트워크 프로토콜을 찾는다 (de-multiplex) 
이때 ethernet 헤더의 ethertype을 사용한다. IPv4면 ethertype이 0x0800이다.
8. ethernet헤더를 제거하고 IP 레이어로 패킷을 전달하게 된다. (IP 레이어는 src ip:port와 dst ip:port)
9.IP layer에서도 패킷이 올바른지 검사하고, (checksum확인) 여기서 IP routing을 해서 패킷을 로컬 장비가 처리하는지
다른 장비로 전달하는지 판단. 로컬 장비가 처리하는 거면 IP헤더의 proto값을 보고 (tcp는 6) 상위 프로토콜
(transport protocol)을 찾는다. 그럼 이제 TCP 레이어로 패킷을 전달한다.
10. 이제 패킷이 올바른지 검사, tcp checksum 확인, 
11. 패킷이 어디에 속하는지 TCP control block을 찾는다.
12. 연결을 찾으면 프로토콜을 수행해서 받은 패킷을 처리한다. 새로운 데이터를 받았다면,
데이터를 receive socket buffer에 추가한다. TCP에 따라 새로운 TCP 패킷을 전송할 수 있다.
13. app이 read system call을 호출하면 커널 영역으로 전환되고, socket buffer에 있는 데이터를 유저 공간의 메모리로 복사해 간다. 복사한 데이터는 socket buffer에서 제거한다. 

<https://blog.packagecloud.io/eng/2016/06/22/monitoring-tuning-linux-networking-stack-receiving-data/>
네트워크 스택에 대한 이야기를 들을 수 있어.

패킷이 도착해서 소켓 receive buffer에 이르기까지는

1. 드라이버가 로드 되고 initialized
2. packet이 NIC로 도착한다.
3. packet is copied (via DMA) to a ring buffer in kernel memory
4. hardware interrupt가 생겨서 시스템이 패킷이 메모리에 들어왔다는 것을 알려(DMA)
5. 드라이버가 NAPI를 불러서 poll loop를 시작해 (만약 실행중이 아니었다면~)
6. ksoftirqd process 가 시스템의 각 CPU에서 돌아가기 시작한다. 그들은 부팅할 때 생기는데, 이 프로세스는
pull packets off the ring buffer by calling the NAPI poll function that the device driver 가등록한 (during initialization)
7. ring buffer의 메모리 영역에서 network data가 쓰여있긴 하지만, 아직 unmapped
8. Data that was DMA'd into memory is passed up the networking layer as an skb for more processing.
9. packet steering ( <https://lwn.net/Articles/362339/>) 이나 NIC의 multiple receive queue를 통해 network data가 distribute된다.
10. network data frame들이 handed to the protocol layers from the queues.
11. protocol layer가 process data
12 data is added to receive buffers attached to sockets by protocol layers. (실제 어플단에서 받나보다)

--packet steering:
현재의 네트워크 하드웨어는 패킷을 옮기지 못하는 수준까지 속도를 올리려고 하는데, 
cpu speed가 증가하는건 멈추고 코어 개수가 늘어나고 있으니, 만약 네트워크 스택이 
하드웨어를 따라갈 수 있게 smarter processing을 ( 여러 코어에 work를 나누는것)
해야한다.
그게 RPS가 나오게 된 배경 (receive packet steering)

OS는 나가는 패킷은 잘 cpu 사이에 distribute가 가능하다. (multiple transmit queue가 지원되기때문)
하지만 들어오는 패킷은 cpu사이에 distribute하기가 힘든데, 왜냐하면 한 NIC에서 들어오기 때문에 그렇다.
어떤 NIC는 들어오는 패킷을 나눌 수 있게 여러 receive queue가 있고 multiple interrupt line이 존재하지만,
single queue만 있는 애들도 있다. 그럼 single stream으로 들어오는 모든 패킷을 드라이버가 처리해야한다는것이다.
그런 stream을 parallelize하는 것은 host OS에 대한 지식을 필요로 한다. 
receive path를 hooking하는 netif_rx()와 netif_receive_skb <- 는 리눅스단의 패킷 
들이 driver가 packet을 networking subsystem에 전달할 때 보는 것이다. 

이제 패킷별로 hash를 통해서 각자가 CPU를 고르게 되어있다. 그럼 target CPU의 자리에 enqueue되게 된다.


### cgroup에 대해서 알아보자
<https://netdevconf.info/1.1/proceedings/slides/rosen-namespaces-cgroups-lxc.pdf>

```
The cgroup (control groups) subsystem is a Resource Management
and Resource Accounting/Tracking solution, providing a generic
process-grouping framework
```
즉, 리소스 관리. (memory,cpu,network) 

cgroup을 위한 별도의 new syscall이 필요하지는 않아..
kernel에 대한 little hook을 본다. (boot phase, fork(), exit(), /proc/pid/cgroup /proc/cgroups 두개 추가.

cgroup core와 (kernel/cgroup.c)
cgroup controller 두개로 이뤄진다. 

cgroup을 mount하기!

cgroup file system을 사용하려면 ( browse를 하거나, attach task to cgroup)
filesystem의 일부에 mount를 해야될 거아니야.
보통 sytstemd나 container project들은 /sys/fs/cgroup
/sys/fs/cgroup/systemd

여기 위치하는데, 
<https://netdevconf.info/1.1/proceedings/slides/rosen-namespaces-cgroups-lxc.pdf> 의 11페이지에 나오는 것과
같은 폴더들이 모여있다. 각각이 모듈이며, memcontrol은 memory_cgrp_subsysㅡ
mm/memcontrol.c 모듈이고,
kernel/sched/cpuacct.c 모듈이 뭔가 cpu 관련인가

이런 인터페이스 파일들이 존재한다. 



<https://blog.packagecloud.io/eng/2016/10/11/monitoring-tuning-linux-networking-stack-receiving-data-illustrated/>
### softirq, linux에서 패킷을 받는것.

컴퓨터 시스템이 어떤 work가 끝났다는 신호를 받으려면, 네트워크의 경우는 NIC가 IRQ를 (kernel interrupt) 
raise해서, packet has arrived and is ready to be processed 임을 알리게 된다.
IRQ handler가 executed by the linux kernel, 그리고 너무 많이 쌓이면 새 IRQ가 만들어지는 것을 막는다.
그러니까 IRQ handlers in device drivers는 무조건 빨리 돌아야한다. 그래서 SOFTIRQ가 만들어져서
이런 handling을 바깥에서 하게 하는 것이다.
softIRQ는 system that kernel uses to process work outside of the device driver IRQ context. 
network devices 의 경우에는, softIRQ system이 responsible for processing incoming packets. 

이런 softIRQ system은 responsible for processing incoming packets. 
즉 device 드라이버가 처리하려면 너무 많으니 다른 쓰레드에 softIRQ를 이용해서 처리한다.
kernel/softirq.c 에서 실행된다.



#### 2020-09-18

두번째 미팅

cgroup이 memory isolation, network isolation이 들어가

그렇다면 softirqd로 처리하기 직전에 memory를 각 버퍼에 할당해줘서 거기로 dma가 갈 수 있게 하는건데
그 메모리할당이 native-native에선 자기걸 쓰니까 바로 이루어질텐데, 컨테이너는 cgroup 에서 지원을 해주기 때문에
늦는 것이 아닌가

교수님의 관점에서는 cgroup의 network isolation이 문제가 있을 것 같다. 조사해보라고 하셨다.

강성민 학생분의 의견은 iperf3 쪽이랑 softirqd를 통해서 캐시 히트가 안나서 속도가 안나는 것일 수도 있다.

softirqd는 일단 패킷을 받는 receiver packet steering RPS 기술때문에 생기는 것은 맞는 것 같다. 

NET namespace for managing network interface


systemd를 이용해서 Cgroup 제어.

systemd는 Linux의 Init Process로, Daemon Process 제어 역할과 더불어 Cgroup을 제어하는 역할도 수행합니다.
systemd의 Cgroup 제어기능은 systemd가 제어하는 Unit의 일부 기능으로 포함되어 있습니다. 여기서 systemd의
Unit은 systemd가 제어하는 Daemon process라고 이해하면된다.
systemd의 Cgroup 제어 기능은 자신이 제어하는 Daemon Process의 resource 사용량을 제어하기 위해 사용된다.


cgroup driver는 cgroup을 관리하는 모듈을 의미한다. 
드라이버는 cgroupfs 와 systemd driver가 존재한다. cgroupfs driver는 직접 cgroupfs로 cgroup를 제어ㅓ,
systemd driver는 systemd를 통해서 Cgroup을 제어한다.


### 20-09-21
<https://netdevconf.info/1.1/proceedings/slides/rosen-namespaces-cgroups-lxc.pdf>
cgroup에 대해서 좀 더알아보자.
일단 각 컨테이너에 프로세서를 할당해버릴 수 있는 것 같은데~

lxc-cgroup -n 컨테이너이름 cpuset.cpus "0,1" 이런식으로?

그러면 cat /sys/fs/cgroup/cpuset/lxc/myfedora/cpuset.cpus 에서 실제배정 cpu 알 수 있네.

그러면 이걸 세팅하니까 이걸 가져다 쓰는 함수가있겠지?

구글 스칼라 에서 논문을 검색할 수 있대.

lxc-cgroup -n myfedora memory.limit_in_bytes 40M
이건 메모리 줄이기
cat /sys/fs/cgroup/memory/lxc/myfedora/memory.limit_in_bytes
41943040
이건 바이트로나옴

이제 release agent 즉 이제 cgroup의 last process가 terminate할때 불리는 가비지 컬렉터 느낌?
echo 1 > /sys/fs/cgroup/memory/notify_on_release
이런식으로, release _ agent가 호출되려면 이게 set 되어 있어야 하겠다.

devcg 가 device control group. 이건 resource controller라기 보다는 access controller이긴해.
enforce restriction on reading, writing and creating(mknod) operations on device files

3 control files: devices.allow, devices.deny, devices.list

devices.allow can be considered as devices white list, deny == black list, list==available devices

그 파일의 entry는 type: can be a(all), c(char device) or b (block device)
Major number, Minor number, Access

/dev/null 의 major number이 1 이고 minor number이 3 


PID cgroup controller가 number of processes per cgroup 을 지정할 수 있나본데

/kernel/cgroup_pids.c 이게 어떻게보는지 모르겠네

cgroup parent에 의해서 controller의 enable과ㅓ dsiable이 결정된다

cgroup controllers 
memory, io , pids 에 대한 support만 있다.

그래서
cgroup.controllers 가 ip memory pids 에 대한 정보만 줄거야.

cgroup.procs는 프로세스들의 PID list를 보여줘. (READ write) 
cgroup.subtree_control

파일시스템이라는게 만들어져서 마운트가 이뤄지면 거기를 이제 그 파일시스템으로 관리할 수 있는거같지
막 mkdir하고 그런거

system의 모든 프로세스는 단 하나의 cgroup에 속한다.
그 프로세스의 모든 쓰레드는 같은 cgroup에 속한다.
프로세스는 cgroup으로 migrate 될 수 있는데, 그 PID를 target cgroup의 cgroup.procs에 쓰면 서 할 수 있다.
all threads of process belong to the same group. 

*모든 프로세스는 migratable하다는거.*

그러면 프로세스에 속한 모든 쓰레드들도 움직인다.
이건 cgroup 1에서는 한 프로세스의 쓰레드가 각각 다른 cgroup에 속할 수 있게 하는 것과는 다르다.
parent가 cgroup 옮겨도 child가 옮겨도 서로 영향안준다.

--path 파라미터에 있는 cgroup name에 기반해서 찾는데, 
cgroup v1에서는 여러 cgroup에 속해있을 수도 있으니 
path로 subgroup을 찾는 게 어려웠는데,
이제는,
예를 들면 "test" 라는 그룹이나 그 서브그룹에서 socket에서 originate되는 트래픽을 찾는 룰은, 
iptalbes -A OUTPUT -m cgroup --path test -j LOG

야. 이이거는 xt_cgroup netfilter match module의 extenstion이다. /net/netfilter/xt_cgroup.c 

test라는 그룹을 만들고, 현재 shell을 거기로 옮기면, 이 쉘에서 만들어지는 모든 소켓은 그 소켓이 만들어진
cgroup 서브그룹에 대한 포인터를 가진다. test 그룹에 대한 포인터!

sock_cgroup_data 오브젝트는, per-socket cgroup information을 가지고 있다.
이건 sock 이라는 오브젝트에 더해진건데, socket이 생성된 cgroup에 대한 포인터를 가지고 있다.

linux의 namespace는
mnt(mount points, filesystems)
pid(processes)
net(network stack)
ipc(System V IPC)
uts (hostname)
user(UIDs)
프로세스는 fork(), clone(), vclone() syscall로 생성가능한데, 이런 네임스페이스를 지원하기 위해 플래그가 더해질 수 있다.

네트워크 네임스페이스는 logically another copy of the network stack, with its own routing tables, firewall rules, and network devices.
자기만의 라우팅 테이블, 방화벽, network device를 갖고있다고?

strcuct net에서 네트워크 테이블과 소켓, procfs sysfs를 다룬다.

```
How do I know to which cgroup does a process belong to?
cat "/proc/$PID/cgroup" shows this info.
• The entry for cgroup v2 is always in the format "0::$PATH".
• So for example, if we created a cgroup named group1 and attached a task
with PID 1000 to it, then running:
cat "/proc/1000/cgroup
0::/group1
And for a nested group:
cat /proc/869/cgroup
0::/group1/nested
```
```
The script in the following slide shows how to connect two namespaces
by veth (Virtual Ethernet drivers) so that you will be able to ping and
send traffic between them

ip netns add netA
ip netns add netB
ip link add name vm1-eth0 type veth peer name vm1-eth0.1
ip link add name vm2-eth0 type veth peer name vm2-eth0.1
ip link set vm1-eth0.1 netns netA
ip link set vm2-eth0.1 netns netB
ip netns exec netA ip l set lo up
ip netns exec netA ip l set vm1-eth0.1 up
ip netns exec netB ip l set lo up
ip netns exec netB ip l set vm2-eth0.1 up
ip netns exec netA ip a add 192.168.0.10 dev vm1-eth0.1
ip netns exec netB ip a add 192.168.0.20 dev vm2-eth0.1
ip netns exec netA ip r add 192.168.0.0/24 dev vm1-eth0.1
ip netns exec netB ip r add 192.168.0.0/24 dev vm2-eth0.1
brctl addbr mybr
ip l set mybr up
ip l set vm1-eth0 up
brctl addif mybr vm1-eth0
ip l set vm2-eth0 up
brctl addif mybr vm2-eth0
```

<https://medium.com/@BeNitinAgarwal/understanding-the-docker-internals-7ccb052ce9fe>
도커는 kernel namespace를 사용해서 컨테이너라는 독립 워크스페이스를 만든다. 
컨테이너가 실행되면, 도커는 그 컨테이너를 위해 set of namespaces를 만든다. 이런 네임스페이스들이
layer of isolation을 제공하게 된다. 각 컨테이너는 separate namespace에서 돌게 되고, 그 네임스페이스에만
엑세스할 수 있다.
또 kernel의 control group을 써서 resource allocation과 isolation을 만들어. 
그걸 하는게 CGROUP이야. 그건 어플리케이션에게 specific set of resource limit을 줄 수 있거든.
control group이 allow docker engine to share available hardware resources to containers and optionally enforce limits and constraints.

net_cls and net_prio cgroup for tagging the traffic control.

```
Docker Engine uses the following cgroups:
Memory cgroup for managing accounting, limits and notifications.
HugeTBL cgroup for accounting usage of huge pages by process group.
CPU group for managing user / system CPU time and usage.
CPUSet cgroup for binding a group to specific CPU. Useful for real time applications and NUMA systems with localized memory per CPU.
BlkIO cgroup for measuring & limiting amount of blckIO by group.
net_cls and net_prio cgroup for tagging the traffic control.
Devices cgroup for reading / writing access devices.
Freezer cgroup for freezing a group. Useful for cluster batch scheduling, process migration and debugging without affecting prtrace.
```
Cgroup을 제어하는 방법은, cgroupfs를 이용하는 방법과 systemd에서 제공하는 API를 사용하는 방법 2가지가 있다. linux의 Cgroup
제어하는 방법 중 하나인 cgroupfs.
Cgroup 정보는linux kernel 안에서 관리. 
Cgroup 정보는 Directory와 File로 나타나고, Cgroup 제어는 Directory 생성, 삭제 및 파일의 내용 변경을 통해서 이루어진다.
따라서, cgroupfs로 Cgroup을 제어할 때는 mkdir, rmdir, echo 와 같은거 사용가능. 
cgroup은 리소스별로 존재해서 리소스별로 mount가 되어있다.

cgroupfs로 Cgroup 생성하는 법은 cgroupfs에 디렉토리 생성. tree형태~
memory cgroup을 만드는것도. 안에 자동적으로 파일이 많이 등장.
메모리 그룹 설정에 사용되는 파일들인거야. cgroup.procs 파일 내용을 보면 어떤 프로세스가 속해있는지 안다.

systemd는 linux의 init process로, systemd가 제어하는 unit의 일부 기능으로 cgroup을 제어할 수 있는 api를 쓸 수있는건가봐.
systemd의 unit은 systemd가 제어하는 데몬 프로세스라고 이해하면 된다.
음 그러니까 systemd의 Cgroup제어 기능은 자기가 원래 Daemon process의 리소스 사용량을 제어해보려고 사용했는데, 이렇게도 쓰는거지


CGroup driver는 cgroup 관리하는 모듈. cgroupfs driver와 systemd driver.
어떤 cgroup driver를 사용할지는 kubelet 과 docker daemon에 설정되며, 둘다 동일한 driver를 써야해.
도커 데몬에 설정된 cgroup driver가 docker daemon과 containerd의 명령에 따라서 실제로 Container 생성을 담당하는 runc가 사용된다.

systemd의 API는 systemd에서 제공하는 IPC기법(Inter process Communication) 중 D-Bus를 통해서 다른 process에게 노출된다.
즉, systemd driver는 D-Bus로 systemd와 통신한다.
systemd는 D-Bus를 통해서 전달된 systemd Driver의 요청에 따라 Cgroup을 제어한다. 

systemd가 Cgroup을 제어할땐 mkdir 같이 cgroupfs 동일하게 사용한다.

systemd가 /sys/fs/cgroup 경로에 cgroupfs를 mount한다고 했었는데, systemd가 cgroupfs를 사용해서 cgroup을 제어하기 때문에 
systemd가 cgroupfs의 mount도 관리하는 것이다. 

pod가 있고 컨테이너가 생성되면 (systemd)
```
/sys/fs/cgroup/memory/kubepods.slice/kubepods-besteffort.slice/kubepods-besteffort-pod0798b0e6_e445_4738_87b6_91bc5cc5e57f.slice/docker-33dff8e50378bb9baa47bccda0b21d57162ac63411e92cd1e0ff6a9a155470a6.scope
```
이런식으로 생긴다.
slice나 scope니 하는 것들이 systemd에서 Cgroup을 관리하기 위한 Unit의 Type을 나타낸 것.


<https://docs.docker.com/network/bridge/>


 도커 네트워크
 도커는 software bridge 를 써서 containers connected to same bridge network. 
 새로 생성된 컨테이너는 거기에 연결된다. 
 그리고 같은 어플리케이션 스택을 브릿지 네트어크에서 실행하면 그 컨테이너끼리는 --link로 직접만들어야된다. 
 그 링크는 양방향으로 만들어져야 한다. /etc/hosts 파일을 컨테이너 사이에 바꿔도 되긴 해~
 
 내 컨테이너들이 default bridge network를 사용하면, 모든 컨테이너가 같은 세팅을 써 MTU, iptable rules. 그래서, default
 bridge network는 도커바깥에서 일어나고, Docker의 restart를 필요로 한다. 
 
```bash
docker create --name my-nginx \
  --network my-net \
  --publish 8080:80 \
  nginx:latest
 ```
 도커 컨테이너만들때, custom network 와 , 컨테이너의 80번포트를 호스트의 8080에 묶어버렸어!
 
 daemon.json에 옵션을 넣어서 default bridge network를 configure 할 수 있어.
 ```
 {
  "bip": "192.168.1.5/24",
  "fixed-cidr": "192.168.1.5/25",
  "fixed-cidr-v6": "2001:db8::/64",
  "mtu": 1500,
  "default-gateway": "10.20.1.1",
  "default-gateway-v6": "2001:db8:abcd::89",
  "dns": ["10.20.1.2","10.20.1.3"]
}
```
오?? 이러고 restart docker하래.
-p 옵션은 그냥 firewall rule하나 추가하는거고, IP주소는
단순히 Docker daemon이 DHCP로 작용해.



docker and iptables

docker은 iptables rule을 이용해 network isolation을 적용한다. 

docker은 installs two custom iptables chains named DOCKER-USER and DOCKER and it ensures that incoming packets are always
checked by these two chains first.

All of Docker's iptables rules are added to the DOCKER chain. 이 chain을 manipulate maunally 해서는 안된다. 만약
뭔가 더하고싶으면, DOCKER-USER chain에 더해라. DOCKER create automatically 한것보다 먼저 docker-user chain이 적용된다.

rules added to the forward chain은 이 도커 체인 두개를 지나야지 적용된다.
만약 도커를 통해 port를 expose했으면, 이 포트는, 내 어떤 firewall이 configure 되었던 간에 docker rule을 따른다.
```
iptables -I DOCKER-USER -i ext_if ! -s 192.168.1.1 -j DROP
```
이러면 ext_if 라는 인터페이스에 192.168.1.1 로 들어오는 패킷을 제외하면
죄다 drop시킨다는 뜻.

```
iptables -I DOCKER-USER -i ext_if ! -s 192.168.1.0/24 -j DROP
```
이러면 192.168.1 서브넷으로 시작하는 애들은 허용하지만 그 외에는 다 드롭

-s가 --src-range -d는 --dst-range

/etc/docker/daemon.json을 만지면 iptables를 도커가 설정못하게 할 수도 있어.

<https://www.netfilter.org/documentation/HOWTO/NAT-HOWTO.html>
linux kernel masquerading NAT
masquerading은 SNAT야. source address를 바꾸니까. 
Destination NAT is when you alter the destination address of the first packet: i.e. you are changing where the connection is going to.
Destination NAT is always done before routing, when the packet first comes off the wire. Port forwarding, load sharing, and transparent proxying are all forms of DNAT.
가장 먼저 이뤄지는건가본데

우리는 NAT rule을 만들어서 kernel에게 어떤 커넥션이 바뀌어야 하고 어떻게 바뀌어야 하는지 말해줘야한다.
그래서 iptables 라는 툴을 이용한다. 그리고 그것에게 말해서 NAT table을 -t nat라고 specify 하도록 한다.

NAT rule 테이블은 three list called chains. 가지고 있다. 각 rule은 examined in order until one matches.
두개는 PREROUTING( destination NAT 패킷이 처음 들어올때,) POSTROUTING (SOURCE NAT, 패킷이 떠날때) , output.
      _____                                     _____
     /     \                                   /     \
   PREROUTING -->[Routing ]----------------->POSTROUTING----->
     \D-NAT/     [Decision]                    \S-NAT/
                     |                            ^
                     |                            |  
                     |                            |
                     |                            |
                     |                            |
                     |                            |
                     |                            |
                     --------> Local Process ------
                     
그렇대 ㅋㅋ

 새 커넥션이면 iptalble chain in the NAT table을 보고, 이미 들어왔던거면 저때 결정된 대로 하게 된다.
 table selection option -t 
 
 -t nat 를 하면 NAT table을 볼 수 있다는 거야 iptable에
 
 -A가 맨 뒤에 APPEND
 -I 가 맨 앞에 insert
 
 -i incoming interface
 -o outgoing interface
 
 
 Source NAT가 -j SNAT로 specify 되는 경우도 있지만, ( 그럼 어디로 나가는 패킷은 src ip를 무엇으로바꿔라 거든)
 
 Masquerading이 specialized case 의 SOURCE NAT야.
 dynamically assigned IP address만을 위해 쓰여, standard dialups
 직접 source address를 명시안해도 ( public ip를 직접 안적어줘도)
 그 패킷이 나가는 interface의 IP를 쓸거야. 그리고 링크가( 커넥션이) 다운되면, 새 IP로 커넥션이 들어올때 glitch가 적어진다.
 
 destination NAT는 PREROUTING chain. 이거도 직접 dest를 명시하기도 해 .
 
 맞아그리고
 SNAT했으면 돌아오는 패킷도 이쪽으로 와야된다는것을 알아야 하잖아. 답장을 일로보내야된다고.
 만약 너가 1.2.3.4 source address 로 보내는 것처럼 패킷을 바꾼다면, (SNAT)
 바깥쪽의 router도 자기가 reply packet (1.2.3.4가 dest인)을 이쪽으로 보내야 한다는 걸 알아야 하잖아
 
 1.만약 너가 SNAT를 이미 하고있던 중이면 암것도 안해도돼
 2. 만약근데 local LAN에서 안쓰던 address로 SNAT를 한다면, (우리가 1.2.3.0/24 네트워크에서 ) 1.2.3.99 아이피로 SNAT했으면,
 너의 NAT box는 ARP request를 보내야 해. ip address add 1.2.3.99 dev eth0 이런식으로 나한테 오게 등록을 해놓을 수도 있고,
 3. 아예 다른 ADDRESS로 snat 하는 거면, 이 NAT box로 돌아올 수 있게 ensure 해주어야 한다. default gateway면 무조건
 그리로 오게되어있으니가 괜찮은데, 아니라면 route 상태를 advertise하거나, 각 머신에 route를 더해주어야한다.
 
 
### 2020-09-23
<https://www.usenix.org/conference/nsdi18/presentation/khalid>
네트워크 스택이해에 도움이되는 논문.

softirqd의 역할과 패킷이 어디에 필요한지 등

흠 가능성이 cgroup이 

```
/sys/fs/cgroup/cpuset/system.slice/
```
에 보니까 docker로 시작하는거 하나있네.
여기에서 cat cpuset.cpus  하니까 0-9로 나온다.
```
sudo docker run -it --cpuset-cpus 1  bruzn/ubuntu-cppthreadserver300 bin/bash
sudo docker exec -it 2b1fec86518c /bin/bash 
```
이렇게하면 cpu 1번만사용한다. 근데 nmon실행시키면 모든 cpu보이긴해서, 다른 cpu에대한 권한은 있는건가? RO?
어쨌든 
cgroup 상에서 cpu하나만 준대

지금 컨테이너는 1만쓸수있느상황에서 (cpu core 1번0
![image](https://user-images.githubusercontent.com/47310668/94021882-79299200-fdef-11ea-9dc4-da7cd49b284f.png)
-A 1,4 했는데 4번에서 ksoftirqd가 겹치니까 성능저하를 발견해냈다. 즉 iperf와 ksoftirq가 같은 코어에 배정받으면
논문대로 iperf3 프로세스를 일부 저해하면서, ksoftirq 즉 커널쪽에서 이 프로세스의 시간을 뺏어버리는 것 떄문인 것 같다.
그리고 1번코어를 쭉 돌았는데 결국 10G가 나오진 않았다. 즉 이건 순전히 운인가?

아니야 일단, 이 논문 내용이 주효한것 같다.
근데 4번코어가 항상 ksoftirqd가 작동하는데 (그래서 iperf3 를 4번코어에서 돌리면 문제가발생함 5.5gb정도로?) 
이부분에 대한 논의가 필요할 것같다.

음 가능한 방법은 일단 우선적으로, Receive packet steering이 잘 안이뤄지고 있는 것이 아닌가 싶다.
![image](https://user-images.githubusercontent.com/47310668/94025530-91031500-fdf3-11ea-9694-a1934f88c6c8.png)

일단 의혹은 , 뭔가 iperf3 패킷이 겹치는게 문제다.

회의결과
NAPI 가 패킷을 한번에 모아서 보내는 batch processing에 관여하는건데
queue에 있는걸 올려주는 역할

#### 2020-09-26

<http://balodeamit.blogspot.com/2013/10/receive-side-scaling-and-receive-packet.html>
hardware device에서 cpu에게 signal을 보내서 device가 input 이나 output operation을 한다고 말해주는거야. (interrupt)
interrupt발생하면, execute an interrupt service routine.

Soft IRQ: 이런 interrupt request is like hardware interrupt request. 
NIC에 packets arrive at NIC an interrupt is generated to CPU so that it can stop whatever it doing. 
그리고 NIC에게 ack을 보내, I am ready to serve you라고 알려준다. 그러면, NIC에서 data를 가져가서, kernel buffer로 copy하고, TCP / IP processing과 provide data to application stack 한다. 
데이터를 TCP / IP stack을 통해 올려보내는 것은, CPU의 poll queue에 softirq로 집어넣는 것이다.

socket buffer pool은 RAM 영역 중, packet data를 가지고 있게 boot up process 에서 할당했던 메모리영역! (kernel memory)

RX queue는 socket descriptors for actual packets in socket buffer pool(위에 설명한). circular queue라서, packet
first arrives at NIC일때, device가 add the packet descriptor in matching Rx queue and its data into socket buffer.
즉 패킷이오면, packet descriptor를 맞는 Rx queue에 넣고, data는 소켓 버퍼에 넣는대.
현대 NIC에서는, multiple queues possible which is also called RSS(concept to distribute packet processing load across multiple processors). 

 이 softirq 가 언제 ksoftirqd를 넘어가냐면
 ```
 <http://egloos.zum.com/rousalome/v/9978671>
 ksoftirqd 스레드는 깨우려면 wakeup_softirqd() 함수를 호출해야 합니다. 이 함수는 다음 조건에서 호출합니다.
 - __do_softirq() 함수에서 Soft IRQ 서비스 실행 중 MAX_SOFTIRQ_TIME 지피 시간만큼 경과했을 때	
 - 인터럽트 컨택스트가 아닌 상황에서 Soft IRQ 서비스를 요청할 때
 ```
 ```
 <https://ghdud4006.tistory.com/7> linux kernel basic 에 관해서 알려준다. 
 * cf ) Polling

;kernel이(processor가) device의 상태를 periodic하게 check

- 장 : polling 시기를 정해 asynchronous한 h/w처리가 발생하지 않음 => 구현 쉬움

- 단 : device가 처리하지 않은 경우도 check하기 때문에 cpu clock 낭비
```

패킷이 NIC에 도착하면, receive queue에 더해진다. Receive queue는 assigned an IRQ number ( 너는 몇번 IRQ야) 
during device driver initialization. 그리고 각 queue마다 available cpu processor가 할당된다.
그 프로세서는 servicing IRQ interrupt service routine에 responsible하다. 
보통, data processing은 also done by same processor which does ISR.(routing말하는 것 같은데?)
너의 기계가 single core면 잘 작동하겠지만, 멀티 코어다 보니까, network traffic 많을 땐 잘 작동 못해.
ISR routine (라우팅 등) 은 너무 작아서 싱글 코어에서 executed 될때는 performance 에 큰 차이가 없지만,
data processing과 moving data up in TCP / IP stack 은 시간이 좀 걸린다. 이게 다 single processor에 의해 돌아가니까.

``` 
<http://balodeamit.blogspot.com/2013/10/receive-side-scaling-and-receive-packet.html>
cat /proc/interrupts 
를 보면 왼쪽이 irq 넘버고 cpu 사용량을 쭉 따라가보면, 어떤 ethernet 카드에 대해서 어떤 core를 쓰고있는 지 알 수 있어.
해당코어에 적혀있는 숫자는 몇개의 인터럽트가 Rx queue에서 생성되었는지.
cat /proc/irq/53/smp_affinity 는 IRQ 53번이 interrupt를 CPU 8 로 보내도록 함을 보여준다.
이건 hexadecimal로 나오는데
1이면 cpu 0 을 뜻하고, value F 는 0~3 FF는 0~7 100은 cpu8 을 뜻함.
```

RSS는 network card가 여러 receive and send queue를 가지고 있도록 한다. 이런 queue들은 individually mapped to each
CPU processor.
```
RSS provides the benefits of parallel receive processing in multiprocessing environments. Receive Side Scaling is a NIC technology. It supports multiple receive queues and integrates a hashing function(distributes packets to different queues by Source and Destination IP and if applicable by TCP/UDP source and destination ports) in the NIC. The NIC computes a hash value for each incoming packet. Based on hash values, NIC assigns packets of the same data flow to a single queue and evenly distributes traffic flows across queues.
```
그렇다는것은,
컨테이너에서 출발한 패킷은 RSS가 적용이안되어서, NIC가 힘들어하는 것이 아닐까??
물론 컨테이너로 들어오는 패킷은 아니다만,
RSS를 하려고 해도 최종목적지를 그 때에 파악못할 것 같으니 RSS 안시키고 보내버리는게 아닐까 싶다.

intel igb driver상에서 multiple queue enable하는 방법을 가지고있다.

### 2020-11-18 

<https://opensource.com/article/20/10/linux-kernel-interrupts>
interrupt에 대한 이야기이다.
interrupt는 hardware interrupt, software interrupt, exception으로 나눠진다.

interrupt request (IRQ)는 programmable interrupt controller (PIC)에 의해 요청이 된다.
이는 CPU를 interrupt 시킴과 executing interrupt service routine (ISR) 하는데에 그 목적이 있다. 
** ISR은 small program인데, process certain data depending on the cause of the IRQ.**
즉 IRQ 종류에 따라 어떤 data를 처리. Normal processing is interrupted until the ISR finishes.
원래 IRQ는 handled by a separate microchip (PIC). PIC가 various hardware IRQ를 manage하고 CPU에게 directly talk. 
IRQ가 일어나면, PIC가 data를 CPU에쓰고, raised interrupt request pin. (INTR) 
그러나 요즘에는
IRQ가 advanced programmable interrupt controller (APIC)에 의해 다뤄진다.


#### HW interrupts:

HW device가 CPU에게 나 이제 process할 준비 됐어 (NIC에 packet이 도착했을때) 라고 하고싶을때.
IRQ를 보내서 signal CPU that data is available. 
이게 커널이 스타트할 때 device driver에 의해 register 되었던 specific ISR을 invoke하게 된다.
This invokes a specific ISR that was registered by the device driver during the kernel's start.

#### sw interrupts
비디오 틀때 music과 video playback을 일치시켜서 music의 speed가 not vary하게 하는 게 중요하다.
이것은 sw interrupt로 accomplish되는데, precise timer system을 이용한다.
이런식으로, software interrupt는 can be invoked by a special instruction to read or write data to a hardware device.

또, sw interrupt는 crucial when real-time capability is required.

#### GET HANDS ON

IRQ는 ordered by priority in a vector on the advanced PIC (APIC where 0==highest priority) 
첫 32 개의 interrupt (0~31)은 CPU에 의해 fixed sequence. <https://wiki.osdev.org/Exceptions> 참고
그 뒤의 IRQ들은 can be assigned differently. 
``` The interrupt descriptor table (IDT) contains the assignment between IRQ and ISR. Linux defines an IRQ vector from 0 to 256 for the assignment.```

registered interrupt를 확인하는 것은 cat /proc/interrupts

왼쪽부터
IRQ vector(숫자)  interrupt count per CPU (0~n번째 CPU까지) | hardware source | hardware source's channel info,
| name of the device that caused the IRQ.

더 아래에 보면 non-numeric interrupts들도 있어. architecture specific interrupts라고 , LOC 같은건 local timer interrupt


<https://github.com/torvalds/linux/blob/master/arch/x86/include/asm/irq_vectors.h>에 어떤 interrupt가 명시되어있다.

``` watch -n1 "cat /proc/interrupts" ``` 로 주기적으로 관찰하자.

<https://0xax.gitbooks.io/linux-insides/content/Interrupts/> linux 책
<https://linux-kernel-labs.github.io/refs/heads/master/lectures/interrupts.html#> linux 깃허브
#### 리눅스의 네트워킹
<https://linux-kernel-labs.github.io/refs/heads/master/labs/networking.html> 네트워크에 대한 공부.
user space에서는 network communication의 abstraction이 socket이야.

IP socket 이 associated with an IP address. 그리고 transport layer protocol (TCP, UDP) 가 사용된다. 포트랑.

##### netfilter:
kernel interface의 이름인데, network packets를 캡쳐해서 modify or analyze them.  (filtering, NAT)
user space에서는 iptables로 사용된다.

리눅스 커널에서는, packet capture using netfilter이 done by attaching hooks.
Hooks 는 can be specified in different locations in the path followed by a kernel network packet. 


### 2020-11-19 미팅
