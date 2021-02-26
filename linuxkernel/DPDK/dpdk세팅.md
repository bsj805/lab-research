
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





