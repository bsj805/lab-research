### 리눅스 커널 코드 분석 (네트워킹)
<https://www.cs.unh.edu/cnrg/people/gherrin/linux-net.html> 
2021 02 16.

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







