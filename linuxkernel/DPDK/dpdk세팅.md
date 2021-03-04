
맨 위글을 기반으로 (인텔 공식문서)
<https://doc.dpdk.org/guides/linux_gsg/sys_reqs.html#compilation-of-the-dpdk>


<https://recordnb.tistory.com/13?category=633474>
<https://jhkim3624.tistory.com/86>

이 사람들의 조언을 받아 해보자


```bash
/sys/kernel/mm/hugepages/hugepages-2048kB$ cat nr_hugepages
0

```


이걸
echo 1024 > /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages
를 이용해 바꾼다.

1024만큼이 필요하다고 하는건가? 응응 2MB 짜리의 huge page 1024개를 reserver하는 거야.

``` bash
wget https://fast.dpdk.org/rel/dpdk-20.11.tar.xz
```
로 다운받아. 

DPDK 설치와 컴파일 과정

1. Hugepage 설정

(1) hugepages=1024

(2) echo 1024 > /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages

(3) mkdir /mnt/huge

(4) mount -t hugetlbfs nodev /mnt/huge

(5) vi /etc/fstab(/etc/fstab 파일에 아래와 같은 설정 추가)

    nodev /mnt/huge hugetlbfs defaults 0 0

cat /proc/meminfo | grep Huge
했을때 hugepages total 이 1024, free가 1024여야한다.
hugepage size는 2048kb짜리.

이제 다운받은 DPDK를 컴파일해보자

####3. Compiling the DPDK target from Source
```bash
root@black-Z10PA-U8-Series:/home/byeon/dpdk-20.11# cat README more
DPDK is a set of libraries and drivers for fast packet processing.
It supports many processor architectures and both FreeBSD and Linux.

The DPDK uses the Open Source BSD-3-Clause license for the core libraries
and drivers. The kernel components are GPL-2.0 licensed.

Please check the doc directory for release notes,
API documentation, and sample application information.

For questions and usage discussions, subscribe to: users@dpdk.org
Report bugs and issues to the development mailing list: dev@dpdk.org

lib: Source code of DPDK libraries

drivers: Source code of DPDK poll-mode drivers

app: Source code of DPDK applications (automatic tests)

examples: Source code of DPDK application examples

config, buildtools: Framework-related scripts and configuration
```


DPDK는 installed on my system using meson and ninja

make config T=x86_64-native-linux-gcc O=mybuild
이걸로 하는건 deprecated
no module named mesonbuild
라는 에러가 뜨는데, 이는 root 계정에서 python3 -m pip install menson 을 하지 않았기때문,
ninja도 마찬가지
그럼 설치가 완료된다.
![image](https://user-images.githubusercontent.com/47310668/109164277-93600580-77bd-11eb-9b37-ec5fd0a01f11.png)
와 같은이미지가 생성.

drivers enabled 목록에 ixgbe가 net driver로 들어가있다.


![image](https://user-images.githubusercontent.com/47310668/109165047-7415a800-77be-11eb-9ef9-d7559194dc7b.png)

이상태에서 ninja
ninja install
ldconfig를 하면, cache를 날리면서, dll를 가져오나보다.
model name      : Intel(R) Xeon(R) CPU E5-2630 v4 @ 2.20GHz 

이게 cpu

cat /proc/cpuinfo


PMD는 poll mode driver의 약자. 

<http://manseok.blogspot.com/2014/11/pmd-dpdk.html>
dpdk 사전정보를 알아야 pmd의 유용성을 알겠다.


#### 5 Linux Drivers

각각 다른 PMD는 (poll mode driver는 require different kernel driver to work properly.
corresponding kernel driver이 load되어야 하고, network ports should be bound to that driver.
즉 포트를 해당 드라이버에 bind 시켜야지만이, 
Different PMDs may require different kernel drivers in order to work properly. Depending on the PMD being used, 
a corresponding kernel driver should be loaded, and network ports should be bound to that driver.


modprobe vfio-pci

PF는 SR-IOV physical function 이고 VF는 SR-IOV virtual function.
Since Linux version 5.7, the vfio-pci module supports the creation of virtual functions. After the PF is bound to vfio-pci module, the user can create the VFs using the sysfs interface, and these VFs will be bound to vfio-pci module automatically.
PF를 vfio-pci module에 bind 시키면, sysfs로 virtual function을 vfio-pci에 자동으로 bind되게 만들 수 있다.

아하, ![image](https://user-images.githubusercontent.com/47310668/109168109-d623dc80-77c1-11eb-9b6d-0e0f8fba21cd.png)
대충 이런걸 그리고 있나본데?

uuid를 호출해서
```
9fa4fc84-7776-11eb-a63c-abab9235515c
```
라는 VF token을 얻었어. UUID는 device를 명칭하는 컴퓨터단위 이름.
즉 PF를 만드니까 거기에 대한 UUID를 구해오는거야. VF에 접근하려면, user는 새토큰을 얻어온대.

byeon에서 하니까
```
de1399bc-7776-11eb-b9c2-2756bcc58463
```

네 계속바뀌는구나.

sriov=1로 enable sriov하고,
![image](https://user-images.githubusercontent.com/47310668/109168950-ad501700-77c2-11eb-8652-4c5b4840f744.png)

그 아래에는 bus:slot.func format으로 쓰는거야.

```
byeon@black-Z10PA-U8-Series:~/dpdk-20.11$ ./usertools/dpdk-devbind.py --status
```
로 확인해서 

Network devices using kernel driver
===================================
0000:03:00.0 'Ethernet Controller 10-Gigabit X540-AT2 1528' if=ens4f0 drv=ixgbe unused=vfio-pci 
0000:03:00.1 'Ethernet Controller 10-Gigabit X540-AT2 1528' if=ens4f1 drv=ixgbe unused=vfio-pci *Active*
0000:05:00.0 'I210 Gigabit Network Connection 1533' if=enp5s0 drv=igb unused=vfio-pci *Active*
0000:06:00.0 'I210 Gigabit Network Connection 1533' if=enp6s0 drv=igb unused=vfio-pci
라는 것을 확인할 수 있었다.
Error: bind failed for 0000:03:00.0 - Cannot bind to driver vfio-pci
Error: unbind failed for 0000:03:00.0 - Cannot open /sys/bus/pci/drivers//unbind

igb도 되긴하는데,

내가 사용하려던건 0000:03:00.1 아 이게 ens4f1이니까, 이게 black에 연결된거고 white쪽은 0000:03:00.0 이니까
내가 white거를 bind하려고해서 error가 난거야.
enp5s0가 public으로나가는애인데, 

근데 지금 active하다고 Warning: routing table indicates that interface 0000:03:00.1 is active. Not modifying
안바꿔주겠대..?
;;;

ifconfig ens4f1 down으로 잠시 inactvie로 바꾼 뒤에 bind해야한대. 
```
First, in order to use network interfaces in dpdk, you need to stop
them. That's why you see 'Routing table indicates that interface
0000:00:08.0 is active. Not modifying' message when you bind them to
igb. You can stop them with 'ifconfig ... down' command.

Second, after you successfully bind at least a pair of ports to igb
driver, they will disappear from ifconfig output as these network
interfaces are no longer controlled by the kernel. That means that the
traffic coming though the interfaces controlled by igb driver should be
handled with custom programmed dataplane that the dpdk application (like
l2fwd) implements.
```
<http://mails.dpdk.org/archives/dev/2015-March/015420.html>
https://github.com/shivarammysore/faucetsdn-intel/blob/master/src/ubuntu/zesty/ovs_281/OVS%20DPDK%20Installation%20and%20Gotchas%20-%20OVS%202017%20Fall%20Conference.pdf

![image](https://user-images.githubusercontent.com/47310668/109170926-97435600-77c4-11eb-9fee-6d702a2427ae.png)

계속 바인딩이 안되는 이유가 여기있는듯.
dmesg를 보니 이런게있네.

dmesg | grep -e DMAR -e IOMMU를 봤을 때
IOMMU가 on 되어있어야 하는데, bios상에서 off되어있다
VT-d도 되어있어야 한다나봐.


https://www.reddit.com/r/linuxhardware/comments/exovc6/where_do_i_add_intel_iommuigfx_off/
를이용해서 iommu=on을 해보았어.



결국 pci_generic으로 갔어.
이걸로 성공

sudo ./dpdk-devbind.py --bind=uio_pci_generic 03:00.1
![image](https://user-images.githubusercontent.com/47310668/109252066-f5595300-782f-11eb-9682-51fd7e8d6020.png)

이렇게된다.
sudo ./build/helloworld -c 4 -n 4
를하면 -c 로 했을땐 bitmap으로 cpu지정해준거라 100. 즉 cpu 2번사용. 
<https://doc.dpdk.org/guides/linux_gsg/build_sample_apps.html> 에 나온다.
 Intel에서는 이 옵션을 VT-d(Virtualization Technology for Directed I/O))라고 부르고 AMD에서는 IOMMU(I/O Memory Management Unit)라고 부른다. 두 경우 모두 새 CPU가 PCI의 실제 주소를 게스트의 가상 주소에 맵핑한다. 이 맵핑이 발생하면 하드웨어가 액세스를 보호하게 되며, 결과적으로 게스트 운영 체제에서는 가상화되지 않은 시스템인 것처럼 장치를 사용할 수 있다. 게스트를 실제 메모리에 맵핑하는 기능 외에도 다른 게스트(또는 하이퍼바이저)의 액세스를 차단하는 분리 기능이 제공된다. [2] => DMA
 <https://frontjang.info/entry/SRIOVSingle-Root-IO-Virtualization%EC%97%90-%EB%8C%80%ED%95%98%EC%97%AC-1-%EC%86%8C%EA%B0%9C>
 
 
 
 즉 가상의 device처럼 쓰게 해주는 VF, pci에 직접연결된 것 처럼 쓰게해주는 PF



VF를 만들면 중간의 VFIO 나 IGB_UIO 이런게 컨테이너와의 연결을 돕는다. 
VFIO는 virtual function IO, UIO는 userspace IO
VFIO는 direct device access to userspace by IOMMU 

SR-IOV는 PCI I/O 가상화. SR-IOV는 VM과 Device를 직접 연결해주는 기술, 
VFIO는 process랑 device를 연결해주는 기술

IOMMU는 DMA access from device가 appropriate memory location으로만 가도록 하는 역할
이게 user level driver가 VFIO를 쓰면서 inappropriate memory에 접근하지 않도록함

리눅스 커널에서 유저 영역에서 직접 장치에 접근할 수 있는 플랫폼을 만들었다.
장치드라이버를 커널에 안두고 유저 영역에 드라이버를 둘 수있는 형태.커

https://jhkim3624.tistory.com/85?category=622798
DPDK는 Data Plane Development Kit의 약자로, Intel 아키텍쳐 기반 고성능 패킷처리 최적화를 위한 시스템 소프트웨어이다. 

DPDK는 크게 Data Plane Library들과 패킷 처리 최적화를 위한 NIC 드라이버의 집합으로 구성되어 있다.



DPDK의 가장 큰 특징은 그림에서 보는 바와 같이 기존 리눅스 기반의 패킷처리과정과는 다르게 커널에서 패킷처리과정을 거치는게 아니라 어플리케이 션이 User Space의 Intel DPDK 라이브러리 API와 EAL(Environment Abstraction Layer)을 사용하여 리눅스 커널을 통과하여 직접 NIC에 엑세스 할 수 있는 통로를 제공한다는 것이다. 

또한, DPDK는 리눅스 User Space의 Data Plane API 뿐만 아니라, 패킷처리에 최적화된 NIC 드라이버를 제공한다.



<https://docs.openstack.org/openstack-ansible-os_neutron/latest/app-openvswitch-dpdk.html>

vfio가 vt_d가 안켜져서였는데 bios에서설정했는데 왜 안켜진다고 하지 했는데 linux boot kernel에서도 vt_d (intel의 iommu) 를 설정해줘야하더라구요

https://docs.openstack.org/openstack-ansible-os_neutron/latest/app-openvswitch-dpdk.html
와 같이 써주어야하는데, 
https://marcokhan.tistory.com/251
처럼 /etc/default/grub 에서 볼 수 있다.

fd03f718-780c-11eb-a306-4f9b4ffd71b6
이걸 --vfio-vf-token EAL파라미터로 DPDK에게 넘겨줘야한다는데 실행할때?

https://github.com/openvswitch/ovs/blob/master/Documentation/intro/install/dpdk.rst#id3
로 실행
export LD_LIBRARY_PATH=/usr/lib/ 이걸 더해주어야했다.


https://software.intel.com/content/www/us/en/develop/articles/using-docker-containers-with-open-vswitch-and-dpdk-on-ubuntu-1710.html
sudo update-alternatives --set ovs-vswitchd /usr/lib/openvswitch-switch-dpdk/ovs-vswitchd-dpdk

https://ubuntu.com/server/docs/openvswitch-dpdk

LD_LIBRARY_PATH (/lib/libbpf.so.0is not a symoblic link error)는 
/etc/ld.so.conf.d 디렉토리에서 ls를 해보면, 공유 라이브러리를 찾는 ld.so 에 대한 디렉토리 목록을 포함한다.
만약 여기에 없으면 LD_LIBRARY_PATH에 검색경로로 디렉토리를 추가해 주고, .bash_profile이나 .bashrc에 추가해준 뒤에
ldconfig로 적용시켜준다. 그래서 ninja 한다음에 ldconfig를 해주는거였어.
원래 내 bashrc에
:/usr/llb/ 도 있었음
/usr/lib에서의 libbpf.0.3.0 에 대한 symbolic link를 /usr/lib64처럼 제작해줌


![image](https://user-images.githubusercontent.com/47310668/109462928-8c7c1000-7aa7-11eb-83b8-3ef234ba3b56.png)


일단 나는 static으로 해봤어.
cd /usr/src/dpdk-20.11
<<https://docs.openvswitch.org/en/latest/intro/install/dpdk/?highlight=dpdk>
이거 기준으로 따라하기.
hugepage 설정은 sudo vi /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages
grep HugePages_ /proc/meminfo 로 찾아볼수있다


mount를 하고, dmesg로 iommu를 확인한다.
dmesg | grep iommu=pt

byeon@black-Z10PA-U8-Series:/etc/sysctl.d$ sudo modprobe vfio-pci
│byeon@black-Z10PA-U8-Series:/etc/sysctl.d$ /usr/bin/chmod a+x /dev/vfio
│/usr/bin/chmod: changing permissions of '/dev/vfio': Operation not permitted
│byeon@black-Z10PA-U8-Series:/etc/sysctl.d$ sudo /usr/bin/chmod a+x /dev/vfio
│byeon@black-Z10PA-U8-Series:/etc/sysctl.d$ sudo /usr/bin/chmod 0666 /dev/vfio/*
│byeon@black-Z10PA-U8-Series:/etc/sysctl.d$ echo $DPDK_DIR
│byeon@black-Z10PA-U8-Series:/etc/sysctl.d$ cd /usr/src/dpdk-20.11


sudo /usr/share/openvswitch/scripts/ovs-ctl start 로
ovs-vsctl: unix:/usr/local/var/run/openvswitch/db.sock: database connection failed (No such 
  system binaries: /usr/local/sbin (--sbindir, OVS_SBINDIR)                                  │file or directory)


이문제해결해보려고했음 -><https://stackoverflow.com/questions/28506053/open-vswitch-database-connection-failure-after-rebooting>
sudo /usr/share/openvswitch/scripts/ovs-ctl start ->여기에 ovs-ctl

나
/usr/local/share/openvswitch/scripts/ovs-ctl start 로 해바. -> 이게 내 $DB_SOCK 에서 db.sock이 가리킬부분.


sudo 할때 PATH에 등록된게 실행이안되는경우:
https://brownbears.tistory.com/252

어 그러니까 된다.

https://ovs-dpdk-1808-merge.readthedocs.io/en/latest/howto/docker.html
에 따라서,
export PATH=$PATH:/usr/local/share/openvswitch/scripts 아까 했었는데
PATH 맨 뒤에 /usr/local/share/openvswitch/python
도 더해주어야한다.

byeon@black-Z10PA-U8-Series:~/ovs$ echo $PATH
/home/byeon/.local/bin:/home/byeon/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/
│bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin:/usr/local/cuda-10.1/bin:/usr/local/cud
a-10.1/bin:/usr/local/cuda-10.1/bin:/usr/local/share/openvswitch/scripts:/usr/local/share/op
envswitch/python

현재 path는 이래야한다.
export PATH=$PATH:/usr/local/cuda-10.1/bin:/usr/local/share/openvswitch/scripts:/usr/local/share/openvswitch/python
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda-10.1/lib64:/usr/lib/
export RTE_SDK=/usr/src/dpdk-20.11/
export RTE_TARGET=x86_64-native-linuxapp-gcc
.bashrc에 지정 

sudo pip3 install FLASK하고,
![image](https://user-images.githubusercontent.com/47310668/109475691-5a73a980-7ab9-11eb-9569-55c18db8299b.png)

이것처럼 cpu 100퍼잡아먹어
ovs를 구성하고 ovs bridge에 dpdk를 붙인 nic를 연결한거야.
<https://ovs-dpdk-1808-merge.readthedocs.io/en/latest/howto/dpdk.html>

![image](https://user-images.githubusercontent.com/47310668/109475839-855dfd80-7ab9-11eb-85c7-b8d48646dc20.png)

lcore mask랑 threadmask를
0x00001 로 해놓은상태
pmd cpumask도 0x00001

See the section Performance Tuning for important DPDK customizations.


어딜보라는걸까.. 
<https://docs.openvswitch.org/en/latest/intro/install/dpdk/?highlight=dpdk>
일단 이거 베이스로 출발하긴했는데,

NIC를 붙이고서는
https://docs.openvswitch.org/en/latest/howto/dpdk/
일단 이거대로?

만약 stall 되는문제가 있다면 /usr/share/openvswitch/scripts 에서 ovs-ctl stop 시키고 해봐
아마 중복된 서버가 있어서 못한걸꺼야.
ovsdb-server.log , ovs-vswitchd.log 로그를 보려면

/usr/local/var/log/openvswitch를 보면돼.

![image](https://user-images.githubusercontent.com/47310668/109652254-e31a4480-7ba2-11eb-959b-cb792662909f.png)
<https://www.youtube.com/watch?v=VXmoyCMyEtA>


ovs-vsctl get Interface dpdk0 statistics  interface이름이 dpdk0인거야.
![image](https://user-images.githubusercontent.com/47310668/109653114-f5e14900-7ba3-11eb-8b26-8c963d3c95a9.png)

흠, 이미지를 보면 ,  <https://arthurchiao.art/blog/ovs-deep-dive-3-datapath/>
OVS에는 2 datapath that I can choose. 
kernel datapath and userspace datapath

먼저 hw에서 packet이 들어오면, datapath를 kernel단에서 보고 해당안되면 system route로 넘기고,
아니라면 netlink dpif 를 참조해서 route info를 찾는다. 혹은 netdev dpif로 handle packet한다.
그걸 dpif로 보내면, vswitchd랑 주고받고, OVSDB랑 주고받아서 끝낸다?



ovs-dpdk는 userspace DATAPATH로 불리운다. 
packet forwarding이랑 processing이 user space에서 이뤄진다.

The Open vSwitch kernel module allows flexible userspace control over flow-level packet processing on selected network devices. It can be used to implement a plain Ethernet switch, network device bonding, VLAN processing, network access control, flow-based network control, and so on.

The kernel module implements multiple datapaths (analogous to bridges -브릿지와 유사하게 ), each of which can have multiple vports (analogous to ports within a bridge 브릿지에 포트를갖고있는 것처럼 ). Each datapath also has associated with it a flow table that userspace populates with flows that map from keys based on packet headers and metadata to sets of actions. The most common action forwards the packet to another vport; other actions are also implemented. 가장 흔한게 packet을 또다른 vport로 forward하는거.


When a packet arrives on a vport, the kernel module processes it by extracting its flow key and looking it up in the flow table. If there is a matching flow, it executes the associated actions. If there is no match, it queues the packet to userspace for processing (as part of its processing, userspace will likely set up a flow to handle further packets of the same type entirely in-kernel)

vport에 packet이 도착하면, kernel module은 flow key를 extract하고, flow table에서 봐서 kernel module이 process한다.
맞는 flow가 있으면 flow table에 정의 된 action을 하고 no match라면, packet을 userspace에 queue해서 process하게 한다. 



OVS bridge는 2 resource를 관리한다. datapath랑 physical or virutal network devices attached to it (netdev) ==network devices

of proto가 OVS bridge implementation이고, 거기에 netdevice가 붙고 그게 physical nic랑 붙나봐
of proto provider도 ovs bridge
datapath management가 dpif, dpif-provider
network devices management ==netdev, netdev-provider

-https://arthurchiao.art/blog/ovs-deep-dive-1-vswitchd/ - ovs source code
![image](https://user-images.githubusercontent.com/47310668/109657902-5a52d700-7ba9-11eb-8668-5497c742ea09.png)

netdev provider의 일부로 DPDK가 있는거다.
netdev provider implements an OS- and hardware-specific interface to "network devices", (NIC == ethernet device)

OVS는 스위치의 각 포트를 netdev처럼 열 수 있다.


OVSdb server가 configureation
/etc/openvswitch/conf.db

OVSDB는 switch-level configuration도 가진다.
bridges, interfaces, tunnel info
<https://arthurchiao.art/blog/ovs-deep-dive-2/>
ovs-vswitchd 에게 OVSDB protocol을 전달한다. 
CLI tools: 
ovs-vsctl : modifies DB by configuring ovs-vswitchd
ovsdb-tool: DB management for example: create/compact/convert DB, show DB logs


OVS patch port는 한 ovs switch port에서 다른 하나로 연결한것과 같다. 즉 linux veth pair같은 것이다.
patch port는 veth pair랑은 달리 cannot capture packets


#### OVS netdev.

network device (physical NIC) has to ends/parts. one end works in kernel, responsible for sending & receiving.
and the other end in userspace, which manages the kernel parts such as changing device MTU size, disabling/enabling queues.
kernel과 userspace 간 communication은 through netlink or ioctl 

##### linux netdev
Linux netdevs are network devices (the userspace part) on Linux platform, call the send() method on a netdev will send the packet from userspace to linux kernel (see linux_netdev_send()), then the packet will be handled by the kernel part (device drivers) of that device. It includes the following three types:
하나의 NIC라고 생각해봐. send를 호출했을때 linux kernel의 syscall이 호출되고, kernel에 의해서 packet이 handle되고.


Actually, a patch port only receives packets from other ports of ovs bridge (ofproto), and the (ONLY?) action for incoming packets from a patch port to datapath, is to “OUTPUT” it to the peer side of this patch port. In this way, it connects the two sides (usually, two OVS bridges).

The “OUTPUT” action just delivers the packet from one vport to another, no memcpy, no context switching, and all work done in datapath, no kernel network stack involved.

Bridge maintains a forwarding table, which stores {src_mac, in_port} pairs, and forwards packets (more accurately, frames) based on dst_mac.


L2 : data link -> dataplane, traffic forwarding
L3 : IP , network controlplane , management,
L4 : transport tcp

internal port가 L3 based고, socket-based이며, (kernel stack based), outside accessible하니까, virtual NIC으로 쓰여서
VM이나 container를 지원해줄 수 있다.

컨테이너들은 각자의 network namespace가 있기 때문에, container를 OVS에 directly connect가 안돼.
default namespace에서나 작용한다. 
그래서 typical way to solve this is to create a veth pair. 한 end를 container에 두고, 다른 end를 OVS에 붙이는방법이었지.

![image](https://user-images.githubusercontent.com/47310668/109664476-832a9a80-7bb0-11eb-81ff-a6c614e47d91.png)
이렇게 말이야.
performance issue가 있어서, 
This is simple and straitforward in concept, but will suffer from performance issues. Could container be connected to OVS directly? The answer is yes! We will use internal port to accomplish this.

container각각에 internal port를 두고, OVS에 그걸 부착하면되지않을까?
정확해.
<https://arthurchiao.art/blog/ovs-deep-dive-6-internal-port/>

#### Connect container to OVS via OVS Internal Port
The main steps are as follows:

get the container’s network namespace, e.g. ns1
create an OVS internal port e.g. with name tap_1
move tap_1 from default namespace to container’s namespace ns1
disable the default network deive in ns1, mostly probably, this is named eth0
configure IP for tap_1, set it as the default network device of ns1, add default route
FINISH
I encapsulated the above procedures into scripts, here is the steps with this scripts:


https://www.44bits.io/ko/post/container-network-2-ip-command-and-network-namespace 


##### faucet
<https://docs.faucet.nz/en/latest/vendors/ovs/README_OVS-DPDK.html>
이거 하려다가 번번히 실패한다.
![image](https://user-images.githubusercontent.com/47310668/109924134-2ab7e200-7d03-11eb-9ae1-3729558b4b1b.png)

그래서 sudo vi ovs-vsctl 해서 이걸 바꿔주었다. 경로를못찾는거같아서


