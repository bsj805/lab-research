### 리눅스 커널 코드 분석 (네트워킹)
<https://www.cs.unh.edu/cnrg/people/gherrin/linux-net.html> 
2021 02 16.
![image](https://user-images.githubusercontent.com/47310668/108203815-57e28d00-7166-11eb-8226-a6604e9f8921.png)

#### 2.1 network traffic path
패킷이 어떻게 이동하는지를 먼저 보자면 , 먼저 IP is the heart of the Linux messaging system.
IP 는 network layer로, TCP 나 UDP가 있는 transport layer 위에 존재한다.


![image](https://user-images.githubusercontent.com/47310668/108159034-868e4280-7129-11eb-8eb9-b61e2e5181ae.png)

app에서 packet을 만들어내면, BSD 소켓에 쓰게되고, BSD socket은 app이 명령한 operation들을 
INET socket의 operation으로 바꾼다. 이런 INET socket은 associated queue와 code가 있어서 
socket operation such as reading, writing ,making connection을 한다. 이는 transport layer과
generic socket 사이의 intermediate layer로서 작용한다. 패킷이 transport layer에 넘어가면,
tcp udp header가 붙고, network layer로 넘어가서 (network layer input function이 실행된다고 표현)
internally forward packet이라면 다시 transport layer- socket- app 순으로 넘어가고,
아니라면, FIB (forwarding information base) 라는 route information을 보고서, 해당 packet을 data link layer (usually ethernet)
로 보내서 패킷을 전송하게 된다.
![image](https://user-images.githubusercontent.com/47310668/108160191-f7365e80-712b-11eb-937c-dfca353f1c0f.png)
sk_buff는 internet, transport, link level에서 use the same socket buffer.

transport protocols(TCP,UDP) create these packet structure (packet을 socket에서 받는애가 transport layer) from output buffers,
while device drivers create them for incoming data.

즉 나갈땐 transport layer에서 output buffer에 들어있는 packet을 sk_buff 형태로 만들고,
들어올 땐 device driver가 만들어주어야 한다. 


#### 2.4 internet routing

IP layer에서 computer 사이의 routing을 관리한다.
세개의 데이터 structure을 관리한다.
1. FIB, track of all the details for every known route.
2. Routing cache for dest. that are currently in use.
3. neighbour table - keeps track of computers that are physically connected to host

 
 FIB는 32 zone을 가지고 있는데, (1111 4개비트로 표현할 수 있는 최대개수인가봐) 
 known destination에 대해 entry를 갖고있다. 각 zone은 contains entries for networks or hosts
 that can be uniquely identified by a certain number of bits.
 ex) netmask of 255.0.0.0 has 8 sig. bits ( 1111 1111 0000~) and would be in zone 8.
 255.255.255.0 has 24 sig bits, would be in zone 24. 
 When IP layer에서 route가 필요하다면, 먼저 해당 존을 찾아가서 entire table을 보며 
 matching 되는 것이 있는지 찾을 것이다. /proc/net/route has the content of the FIB
![image](https://user-images.githubusercontent.com/47310668/108161092-ac1d4b00-712d-11eb-9644-1d67e5284e6e.png)

라우팅 캐시는 /proc/net/rt_cache 만약 여기 256 entry 중 appropriate route가 없으면 FIB에서 찾아서 새
entry를 넣는다. time out 되면 IP에서 deletes it. 
다른 프로토콜 (RIP) 도 같은 구조를 띈다. kernel의 existing table을 ioctl() 함수를 통해서 바꿀뿐.
#### 3. network initialization.

#### 3.1 overview.
 부팅할때 configuration을 읽는데, 이걸로 own address를 determine하고, initialize its interfaces (NICs or so) 
and add critical and known static routes, (internet으로 연결되는라우터라던지)

2월 17일 
이도현 박사과정님의 세미나

![image](https://user-images.githubusercontent.com/47310668/108169351-f279a680-713b-11eb-912f-27b6496daf0c.png)
DPDK는 BSD 소켓과는달리 메모리 풀에서 alloc이 되는 구조라고한다.
그래서 정해진 개수의 버퍼들만 사용할 수 있다. 하지만 빠르다는 장점이 있는 것.
그걸 closed 모델 
BSD는 패킷을 받을 때 malloc 즉 운영체제단에서 메모리할당을 해야하기 때문에 느리다. 

초기 initialize 이후에 alloc이나 free가 이뤄지지않고 계속 단계사이에서 돌아다니는 것을 하자는
Tiny NF

#### 3.2 startup

linux가 os로서 부팅되면, disk에서 이미지를 로드해서 메모리에 넣은다음, unpack하구, kernel의 booting시
마지막 initialization task는 init program을 실행시키는 것. 이 프로그램은 /etc/inittab의 configuration file을 읽어서
redhat에선 /etc/rc.d 에 있는 startup script를 실행시킨다. 이 스크립트는 다른 스크립트를 실행시키면서 
network script (/etc/rc.d/init.d/network) 를 실행시킨다. 

#### 3.2.1 network initialization script

network initialization script는 environment variable을 설정해서 host computer를 identify 하고 네트워크의 사용여부를 판단한다.
네트워크 트래픽을 보낼 디폴트 라우터 설정이나 device to use to send such traffic 
그 다음 ifconfig랑 route program을 사용해서 network device를 가져온다 (brings up) 이 단계에서 DHCP 서버에 query하기도함.
이게 dynamic environment( 타 사용자들의 주소를 동적으로 받는경우)

리눅스에선 보통 많은 양의 스크립트를 실행시켜서 machine setup을 돕는다. 
네트워크 스크립트가 끝나면 FIB는 특정 호스트나 네트워크에 대한 route를 가지고 있고, routing cache나 neighbour table은 empty
Traffic이 flow하기 시작하면, kernel은 그 빈 곳을 채우겠지. 

#### 3.2.2 ifconfig

ifconfig는 어떤 interface device를 쓸 지 configure한다. 각 device에 IP 주소를 주고, netmask를 주고, boradcast address를 provide한다.

device는 각자 initialization function을 실행하고, register its interrupts and service routines with the kernel.
어떻게 해줘야하는지를 등록한다. 

인터페이스는 각각 commandline에서 setting을 바꿀 수 있고 (ifconfig로) 

"route"프로그램은 simply adds predefined routes for interface devices to FIB
can also delete routes.

/etc/sysconfig/network-scripts/ifcfg-lo
이게 loopback device configuration 인데, inter-process communication을 위해 모든 컴퓨터는 세팅을 해야해.


/etc/sysconfig/network 에 설정된게 부팅될 때 처음 설정 된 것.
이 variable을 setting하면, file은 ethernet card를 위한 env var을 설정한다. 네트워크 스크립트가 네트워크 디바이스를 configure하는 것.
네트워크 스크립트는 ifconfig program을 run 해서 device를 start 시킨다. 마지막으로 스크립트는 route program을 실행시켜서
default gateway (route)를 추가하고, /etc/sysconfig/static-routes 파일의 route를 추가한다. 

#### 3.3.3 network routing computer
이건 우리의 경우는 아니다. 위의 네트워크 연결상태를보면, 모든 lan 사용자들은 (cs.u.edu subnet) 
viper interface로 들어가 dodge interface를 통해 인터넷과 연결된다. 그를 위한 네트워크 세팅이다.


####  4.2 socket structure

<https://www.kernel.org/doc/htmldocs/networking/API-struct-socket.html>
와 같이 struct socket 에 대한 설명이 있는데,
struct socket {
  socket_state state;
  short type;
  unsigned long flags;
  struct socket_wq __rcu * wq;
  struct file * file;
  struct sock * sk;
  const struct proto_ops * ops;
};  

*ops 이 친구가 contains pointers to protocol specific functions for implementing general socket behavior.

즉 sendmsg() 이런걸 socket에서 실행시키려면 프로토콜 별로 다른 함수가 define 되어있을 텐데, 그걸 다르게
point하게 해서 inet_sendmsg()를 부를 수 있게 한다. ops->sendmsg 는 inet_sendmsg()를 point하게 하듯.

struct file은 struct inode를 가지고 있는데 파일 inode를 가리키게 해서, 이 socket이랑 함께 associate된 파일을 가리킨다.

이건 BSD 소켓이야.
struct sock *sk 이것이 inet socket이야. INET socket이 BSD 소켓과 합쳐져있는것.
Inet socket이 struct sock에 속해있는데, #include/net/sock.h 에 있다.
<https://www.kernel.org/doc/htmldocs/networking/API-struct-sock.html>





#### 5. sending messages
![s_tx](https://user-images.githubusercontent.com/47310668/108613356-85645a80-7434-11eb-8d3e-9055e94cd58f.jpg)

socket 생성될 때 packet buffer가 생성되는데,
socket의 struct 중 protocol 이라고 header부분이 있어. 그 헤더를 채워넣으면 TCP 단에서 skbuf가 생성된 것.
이걸 이제 IP layer (network layer) 로 보내면 IP도 자기 header를 채워넣고 하겠지. ( skbuf에서 IP header 변수와 tcp header변수가있어서 채워넣기만 하면돼. 또 다른 패킷을 만드는게아니라)

아 그 패킷을 우리가 struct sk_buff skb라고 표현했잖아. 이게 socekt buffer야. data를 담고있을 수 있잖아.
그래서 transport layer 에서 socket buffer을 create해서 outgoing packet을 이 new buffer에 application buffer의 데이터를 copy해 오고, 

app에서 System call이 socket에 data를 쓰는데, 이걸로 transport layer에가서 skbuf (socket buffer)가 생성된다는 거지.
IP layer에서 fragment the packet if required.?

IP layer (network layer)에서 link layer 함수로 패킷을 전달하는데, 이 link layuer함수는 packet을 sending device의 xmit queue (transmission queue 전송 queue, rx queue가 수신큐) 
and makes sure the device knows that it has traffic to send. 이게 IRQ중 하나겠지? 
마지막으로, device (NIC) tells the bus to send the packet.

#### 5.2 Sending Walkthrough

##### 5.2.1 writing to socket.
app layer에서 socket에 data를 작성,
socket은 location of data를 이용 message header를 채운다.
socket의 상태확인
INET SOCKet의 함수를 실행시켜서 pass the message header.
___________________________
socket buffer인 skbuf를 만드는 것은 UDP나 TCP나 , 역시 transport layer.?
UDP는 header만 create한다고 써있긴한데, UDP는 IP build, transmit function을 부른다.
TCP는 skbuf를 만들고,(packet buffer) user space로부터 payload를 copy해오고, packet을 outbound queue에 추가하고, ACK SYN 같은 tcp header를 넣고,
call IP transmit function


IP layer에서는 UDP의 경우packet buffer을 생성해주고, TCP의 경우에는 있는 route to destination을 확인하고, fill in the packet IP header.
copy transport header and payload from user space, send packet to the dst route's device output function.
이제 data link layer. NIC 에서는 packet을 device output queue에 넣었고, 
wake the device하고, device driver에서 scheduler가 run하기를 기다린다음, test the device.
Link header를 전송, bus를 통해서 transmit packet.

#### 6. Receiving Messages

![r_rx](https://user-images.githubusercontent.com/47310668/108688522-5dabea00-753b-11eb-9ba0-a7eb0cfc21ec.jpg)
incoming message는 medium에 packet이 도착하면서 device가 메세지가 준비되었다는 interrupt를 보내면서 시작된다

왼쪽 아래 모서리가 시작점이 되는데, Device는 storage space를 allocate 해서 bus에게 message를 그 공간에 넣으라고 한다.
그러면 packet을 link layer로 올리고, link layer은 패킷을 backlog queue에 넣는다. 
그다음 'bottom-half' 가 실행되도록 하는데, 이는 리눅스 시스템 중 하나로, interrupt 동안 처리되는 work를 minimize할 수 있다.
interrupt 동안 많은 processing을 하는게 좋은 일이 아니다. running process를 방해하기 때문. 대신, interrupt handler는 top-half와 bottom-half를 가지고 있어서,
interrupt가 도착했을 때 top-half 가 run 하며 device queue에서 kernel memory로 옮기는 정도의 일을 하고, 
scheduler에 의해 시간을 받게 되면, bottom half가 실행될 수 있는 것이다.

packet이 NIC에 닿으면, device는 ethernet header를 체크 해서, 패킷을 저장한다. 그 패킷을 kernel memory (backlog queue) 에 옮기면 top half가 끝나는 것이다.

Scheduler에 의해 시간을 받으면, bottom half가 run 되는데,
backlog queue에서 packet을 pop 해서, known protocol (typically IP) 로 match 한 다음, 해당 protocol 의 receive function을 호출한다.
IP layer는 해당 패킷의 error를 체크한다음, route하거나 ( 다른 ongoing queue로 가), transport layer의 TCP나 UDP 함수를 호출하게 된다.  
TCP나 UDP 단에서는 다시 에러를 체크하고, 패킷에 명시된 port와 associate 된 socket을 look up 한다음, 해당 socket의 receive queue에 packet을 넣는다.
Socket queue 에 packet이 들어온 다음, socket은 app process를 wake up 시켜서, read syscall 에서부터 return을 받고, (blocked syscall이라면) 
queue로 부터 its own buffer에 packet의 데이터를 집어넣는다. 
받을 때의 defragmentation은 ip_rcv()

#### 7 IP forwarding

![image](https://user-images.githubusercontent.com/47310668/108701034-cb134700-754a-11eb-8a40-211395c5872c.png)

위와는 달리 다른 host로 가는 패킷을 받은 경우이다.
Forwarded packet은 interrupt from device로 부터 온다. Device는 storage space를 allocate 하고, tells the bus to put the message into that space. (Skbuf로 추정) 
그런다음 link layer로 보내서, backlog queue에 넣고, returns control to the current process. 현재의 프로세스는 interrupt 받고 있었으니 다시 돌려주는거 권한.

#### 8 Basic IP Routing

라우팅을 어떻게 하는지, 어떻게 routing table이 세워지고 업데이트되는지,를 알려준다.
라우팅엔 세가지 종류
Neighbour table: ethernet으로 직접 연결되어있는  (directly connected via LAN)
two for IP networking
FIB table, Routing cache.

![image](https://user-images.githubusercontent.com/47310668/108706493-0b29f800-7552-11eb-9caf-58cf60544536.png)


Neighbor table은 어떤 device가 어떤 protocol로 연결되어있는지 정보를 가진다. Linux는 ARP (address resolution protocol)을 이용해서 maintain and update the table.
따라서 일정기간동안 안 쓰면, 사라지게 만들 수도 있다. entry에서.


이런 table들에서 u32 (host byte order) and _u32 (network byte order_)로 어림짐작이 가능하다.ntohl 이런함수 쓰는이유
#### 9 Dynamic routing with routed

어디로 패킷을 보내야하는 지 알아야되는 routing의 역할을 해야할 때에

#### 10 Editing Linux Source code

#### 10.1 Linux Source Tree

리눅스의 source 
code는 /usr/src directory에 위치하게 된다. 하나의 soft link 가 존재하게 된다. 현재 버전의 코드에.
/usr/src/linux/에 overview of directory structure 설명이 써져있다.
















