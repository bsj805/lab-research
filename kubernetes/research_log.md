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

각 코어에서 어떤 프로세스가 일어나는건지 알아볼 수있는 시간이!

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
numactl -C 4 iperf3  를 하는 것과 똑같다고한다.

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
