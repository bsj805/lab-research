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

tcpdump -c 30 -i ens4f1 -N 해야지 name으로안나온다. -A였나?

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
NIC가 패킷을 메모리에 기록하고, CRC로 패킷이 올바른지 검사하고, 호스트의 메모리 버퍼로 전송한다.
버퍼는 NIC 드라이버가 커널에 요청해서 미리 패킷 수신용으로 할당한 메모리고, 할당받은 후에 드라이버는 NIC에 메모리 주소와 크기를 알려준다.
만약 NIC가 패킷을 받았는데 할당된 메모리가 없으면 NIC가 패킷을 drop 시킨다.

패킷을 호스트메모리로 전송시키면 NIC가 호스트 OS에 인터럽트를 보낸다. 
드라이버가 새로운 패킷을 보고 자신이 처리하는 패킷인지 검사.
드라이버가 상위 레이어로 패킷을 전달하려면, 운영체제가 사용하는 패킷 구조체로 포장해야한다.
linux의 sk_buff (아 이게 skb네) 가 운영체제의 패킷구조체이다. 드라이버가 이렇게 포장한 패킷을 상위 레이어로 전달한다. 

ethernet layer에서도 패킷이 올바른지 검사하고, 상위 네트워크 프로토콜을 찾는다 (de-multiplex) 
이때 ethernet 헤더의 ethertype을 사용한다. IPv4면 ethertype이 0x0800이다.

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
9. packet steering ( 
